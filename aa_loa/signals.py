# Django
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LeaveOfAbsence
from .tasks import send_loa_webhook, sync_loa_groups


@receiver(post_save, sender=LeaveOfAbsence)
def on_loa_saved(sender, instance, created, **kwargs):
    if created:
        send_loa_webhook.delay(instance.id)

    # Trigger a sync immediately so if it's active today, they get the role
    sync_loa_groups.delay()
