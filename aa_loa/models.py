# Django
from django.contrib.auth.models import Group, User
from django.db import models
from django.utils import timezone


class LOAConfig(models.Model):
    loa_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The Django Group to assign to users while their LOA is active.",
    )
    discord_webhook_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional Discord Webhook URL for Director notifications when LOAs are created.",
    )

    class Meta:
        verbose_name = "LOA Config"
        verbose_name_plural = "LOA Config"

    def __str__(self):
        return "Leave of Absence Configuration"


class LeaveOfAbsence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loas")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proxy_loas",
        help_text="If submitted by a Director, this logs who did it.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_revoked = models.BooleanField(
        default=False, help_text="Set to true if the user returned early."
    )
    notified_return = models.BooleanField(
        default=False,
        help_text="Set to true once the welcome back notification is sent.",
    )

    class Meta:
        permissions = (
            ("basic_access", "Can access the LOA module"),
            ("manage_loa", "Can manage LOAs for other users and view HR dashboard"),
        )
        ordering = ["-start_date"]

    def __str__(self):
        return f"LOA: {self.user.username} ({self.start_date} to {self.end_date})"

    @property
    def is_active(self):
        if self.is_revoked:
            return False
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def is_past(self):
        if self.is_revoked:
            return True
        today = timezone.now().date()
        return self.end_date < today

    @property
    def is_future(self):
        if self.is_revoked:
            return False
        today = timezone.now().date()
        return self.start_date > today
