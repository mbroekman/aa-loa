# Django
from django.apps import AppConfig


class LoaConfig(AppConfig):
    name = "aa_loa"
    label = "aa_loa"
    verbose_name = "Leave of Absence"

    def ready(self):
        # AA Industry App
        import aa_loa.signals  # noqa: F401
