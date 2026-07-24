from django.contrib import admin

from .models import LeaveOfAbsence, LOAConfig


@admin.register(LOAConfig)
class LOAConfigAdmin(admin.ModelAdmin):
    list_display = ["__str__", "loa_group"]


@admin.register(LeaveOfAbsence)
class LeaveOfAbsenceAdmin(admin.ModelAdmin):
    list_display = ["user", "start_date", "end_date", "is_active", "is_revoked"]
    list_filter = ["is_revoked", "start_date", "end_date"]
    search_fields = ["user__username"]
