from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DirectorLOAForm, PlayerLOAForm
from .models import LeaveOfAbsence
from allianceauth.notifications import notify


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
        notify(
            user=loa.user,
            title="Leave of Absence Cancelled",
            message=f"Your Leave of Absence starting on {loa.start_date} was cancelled by HR ({request.user.username}).",
            level="warning"
        )
    return redirect("aa_loa:hr_dashboard")

@login_required
@permission_required("aa_loa.manage_loa")
def loa_hr_dashboard(request):
    all_loas = LeaveOfAbsence.objects.all().select_related("user").order_by("-start_date")
    
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
        {"loas": all_loas, "form": form},
    )
