from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from aa_loa.models import LeaveOfAbsence


class LeaveOfAbsenceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.today = timezone.now().date()
        self.tomorrow = self.today + timedelta(days=1)
        self.yesterday = self.today - timedelta(days=1)

    def test_active_loa(self):
        loa = LeaveOfAbsence.objects.create(
            user=self.user,
            start_date=self.yesterday,
            end_date=self.tomorrow,
            reason="Vacation"
        )
        self.assertTrue(loa.is_active)
        self.assertFalse(loa.is_past)
        self.assertFalse(loa.is_future)

    def test_future_loa(self):
        loa = LeaveOfAbsence.objects.create(
            user=self.user,
            start_date=self.tomorrow,
            end_date=self.tomorrow + timedelta(days=5),
            reason="Upcoming trip"
        )
        self.assertTrue(loa.is_future)
        self.assertFalse(loa.is_active)
        self.assertFalse(loa.is_past)

    def test_past_loa(self):
        loa = LeaveOfAbsence.objects.create(
            user=self.user,
            start_date=self.yesterday - timedelta(days=5),
            end_date=self.yesterday,
            reason="Old trip"
        )
        self.assertTrue(loa.is_past)
        self.assertFalse(loa.is_active)
        self.assertFalse(loa.is_future)

    def test_revoked_loa(self):
        loa = LeaveOfAbsence.objects.create(
            user=self.user,
            start_date=self.yesterday,
            end_date=self.tomorrow,
            is_revoked=True
        )
        # Even if dates overlap, a revoked LOA is technically not "active" in standard business logic
        # But our property checks just dates and is_revoked.
        self.assertFalse(loa.is_active)
