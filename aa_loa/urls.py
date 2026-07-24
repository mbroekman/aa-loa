from django.urls import path

from . import views

app_name = "aa_loa"

urlpatterns = [
    path("", views.loa_index, name="index"),
    path("revoke/<int:loa_id>/", views.revoke_loa, name="revoke"),
    path("hr/", views.loa_hr_dashboard, name="hr_dashboard"),
]
