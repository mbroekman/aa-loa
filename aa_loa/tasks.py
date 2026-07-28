# Standard Library

# Third Party
import requests
from celery import shared_task

# Django
from django.db import models
from django.utils import timezone

# Alliance Auth
from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

from .models import LeaveOfAbsence, LOAConfig

logger = get_extension_logger(__name__)


@shared_task
def sync_loa_groups():
    """
    Checks all LOAs and adds/removes users from the designated LOA Django group.
    """
    config = LOAConfig.objects.first()
    if not config or not config.loa_group:
        logger.warning("LOA Config or LOA Group is not set. Cannot sync groups.")
        return

    loa_group = config.loa_group
    today = timezone.now().date()

    # 1. Add users with active LOAs
    active_loas = LeaveOfAbsence.objects.filter(
        start_date__lte=today, end_date__gte=today, is_revoked=False
    )
    for loa in active_loas:
        if not loa.user.groups.filter(id=loa_group.id).exists():
            loa.user.groups.add(loa_group)
            logger.info(f"Added {loa.user.username} to LOA Group.")

    # 2. Remove users whose LOAs have ended or been revoked,
    # but ONLY if they don't have another overlapping active LOA.
    inactive_loas = LeaveOfAbsence.objects.filter(
        models.Q(end_date__lt=today) | models.Q(is_revoked=True)
    )

    for loa in inactive_loas:
        user = loa.user
        # Check if they have another active LOA right now
        has_active = LeaveOfAbsence.objects.filter(
            user=user, start_date__lte=today, end_date__gte=today, is_revoked=False
        ).exists()

        if not has_active and user.groups.filter(id=loa_group.id).exists():
            user.groups.remove(loa_group)
            logger.info(f"Removed {user.username} from LOA Group.")

            # Send Welcome Back Notification if not sent
            if not loa.notified_return and loa.end_date < today and not loa.is_revoked:
                message_text = "Welcome back! Your LOA has expired. Let us know if you need an extension."
                notify(
                    user=user,
                    title="Welcome Back from LOA",
                    message=message_text,
                    level="info",
                )

                try:
                    # Django
                    from django.conf import settings

                    if "aadiscordbot" in settings.INSTALLED_APPS:
                        # Third Party
                        from aadiscordbot.tasks import send_direct_message_by_user_id

                        send_direct_message_by_user_id.delay(
                            user.pk, f"**Welcome Back from LOA**\n{message_text}"
                        )
                except Exception as e:
                    logger.error(f"Failed to send Welcome Back DM: {e}")
                loa.notified_return = True
                loa.save(update_fields=["notified_return"])


@shared_task
def send_loa_webhook(loa_id):
    """
    Sends a Discord webhook notification when a new LOA is submitted.
    """
    config = LOAConfig.objects.first()
    if not config or not config.discord_webhook_url:
        return

    try:
        loa = LeaveOfAbsence.objects.get(id=loa_id)
    except LeaveOfAbsence.DoesNotExist:
        return

    title = "New Leave of Absence"
    if loa.submitted_by:
        title = f"Proxy LOA submitted by {loa.submitted_by.username}"

    embed = {
        "title": title,
        "color": 16753920,  # Orange
        "fields": [
            {"name": "Player", "value": loa.user.username, "inline": True},
            {"name": "Start", "value": str(loa.start_date), "inline": True},
            {"name": "End", "value": str(loa.end_date), "inline": True},
        ],
    }

    if loa.reason:
        embed["fields"].append(
            {"name": "Reason", "value": loa.reason[:1000], "inline": False}
        )

    payload = {"embeds": [embed]}
    try:
        requests.post(config.discord_webhook_url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Failed to send LOA webhook: {e}")
