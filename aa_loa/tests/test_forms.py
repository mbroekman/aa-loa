# Standard Library
from datetime import timedelta

# Django
from django.test import TestCase
from django.utils import timezone

# AA Industry App
from aa_loa.forms import PlayerLOAForm


class PlayerLOAFormTest(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

    def test_valid_form(self):
        form_data = {
            "start_date": self.today,
            "end_date": self.tomorrow,
            "reason": "Test reason",
        }
        form = PlayerLOAForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_start_date_in_past(self):
        form_data = {
            "start_date": self.yesterday,
            "end_date": self.tomorrow,
            "reason": "Test reason",
        }
        form = PlayerLOAForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("start_date", form.errors)

    def test_end_date_before_start_date(self):
        form_data = {
            "start_date": self.tomorrow,
            "end_date": self.today,
            "reason": "Test reason",
        }
        form = PlayerLOAForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)  # Raised as a non-field error by clean()
