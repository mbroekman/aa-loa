# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext

# Alliance Auth
from allianceauth.notifications import notify

from .discord_i18n import discord_language, user_language
from .forms import DirectorLOAForm, LOAConfigLanguageForm, PlayerLOAForm
from .models import LeaveOfAbsence, LOAConfig


@login_required
@permission_required("aa_loa.basic_access")
def loa_index(request):
    user_loas = LeaveOfAbsence.objects.filter(user=request.user).order_by("-start_date")

    if request.method == "POST":
        form = PlayerLOAForm(request.POST)
        if form.is_valid():
            loa = form.save(commit=False)
            loa.user = request.user
            loa.save()
            messages.success(request, "Leave of Absence submitted successfully.")
            return redirect("aa_loa:index")
    else:
        form = PlayerLOAForm()

    return render(
        request,
        "aa_loa/index.html",
        {"loas": user_loas, "form": form},
    )


@login_required
@permission_required("aa_loa.basic_access")
def revoke_loa(request, loa_id):
    loa = get_object_or_404(LeaveOfAbsence, id=loa_id, user=request.user)
    if request.method == "POST":
        loa.is_revoked = True
        loa.save()
        messages.success(request, "LOA cancelled/revoked.")
    return redirect("aa_loa:index")


@login_required
@permission_required("aa_loa.manage_loa")
def hr_revoke_loa(request, loa_id):
    loa = get_object_or_404(LeaveOfAbsence, id=loa_id)
    if request.method == "POST":
        loa.is_revoked = True
        loa.save()
        messages.success(request, f"LOA for {loa.user.username} cancelled by HR.")
        # In the member's own language, not the HR officer's.
        with discord_language(user_language(loa.user)):
            title = gettext("Leave of Absence Cancelled")
            message_text = gettext(
                "Your Leave of Absence starting on %(start)s was cancelled by HR "
                "(%(by)s)."
            ) % {"start": loa.start_date, "by": request.user.username}
        notify(
            user=loa.user,
            title=title,
            message=message_text,
            level="warning",
        )

        try:
            # Django
            from django.conf import settings

            if "aadiscordbot" in settings.INSTALLED_APPS:
                # Third Party
                from aadiscordbot.tasks import send_direct_message_by_user_id

                send_direct_message_by_user_id.delay(
                    loa.user.pk, f"**{title}**\n{message_text}"
                )
        except Exception:
            pass
    return redirect("aa_loa:hr_dashboard")


@login_required
@permission_required("aa_loa.manage_loa")
def loa_hr_dashboard(request):
    all_loas = (
        LeaveOfAbsence.objects.all().select_related("user").order_by("-start_date")
    )

    # Calculate metrics for the overview cards
    active_count = sum(1 for loa in all_loas if loa.is_active)
    future_count = sum(1 for loa in all_loas if loa.is_future)
    total_count = len(all_loas)

    if request.method == "POST":
        form = DirectorLOAForm(request.POST)
        if form.is_valid():
            loa = form.save(commit=False)
            loa.submitted_by = request.user
            loa.save()
            messages.success(request, f"Proxy LOA submitted for {loa.user.username}.")
            return redirect("aa_loa:hr_dashboard")
    else:
        form = DirectorLOAForm()

    return render(
        request,
        "aa_loa/hr_dashboard.html",
        {
            "loas": all_loas,
            "form": form,
            "active_count": active_count,
            "future_count": future_count,
            "total_count": total_count,
            "language_form": LOAConfigLanguageForm(
                instance=LOAConfig.objects.first() or LOAConfig()
            ),
        },
    )


@login_required
@permission_required("aa_loa.manage_loa")
def hr_discord_language(request):
    """Save the language of the LOA webhook messages (HR dashboard)."""
    config = LOAConfig.objects.first() or LOAConfig()
    if request.method == "POST":
        form = LOAConfigLanguageForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, gettext("Discord message language saved."))
    return redirect("aa_loa:hr_dashboard")
