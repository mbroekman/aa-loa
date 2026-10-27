# Standard Library
from datetime import timedelta
from unittest.mock import patch

# Django
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone, translation

from aa_loa.discord_i18n import channel_language, default_language, user_language
from aa_loa.models import LeaveOfAbsence, LOAConfig
from aa_loa.tasks import send_loa_webhook


class LanguageChoiceTest(TestCase):
    @override_settings(LANGUAGE_CODE="en-us")
    def test_default_falls_back_to_language_code(self):
        self.assertEqual(default_language(), "en-us")

    @override_settings(DISCORD_MESSAGE_LANGUAGE="nl", LANGUAGE_CODE="en-us")
    def test_default_uses_the_discord_setting(self):
        self.assertEqual(channel_language(""), "nl")
        self.assertEqual(channel_language("de"), "de")

    @override_settings(DISCORD_MESSAGE_LANGUAGE="en")
    def test_user_language_or_default(self):
        user = User.objects.create_user(username="lang")
        self.assertEqual(user_language(user), "en")
        user.profile.language = "nl"
        self.assertEqual(user_language(user), "nl")


@patch("aa_loa.signals.send_loa_webhook.delay")
@patch("aa_loa.signals.sync_loa_groups.delay")
class LoaWebhookLanguageTest(TestCase):
    def _loa(self):
        user = User.objects.create_user(username="pilot")
        today = timezone.now().date()
        return LeaveOfAbsence.objects.create(
            user=user, start_date=today, end_date=today + timedelta(days=3)
        )

    @patch("aa_loa.tasks.requests.post")
    def test_webhook_uses_the_configured_language(self, post, *_signals):
        LOAConfig.objects.create(
            discord_webhook_url="https://discord.test/hook", discord_language="nl"
        )
        loa = self._loa()
        with translation.override("en"):
            send_loa_webhook(loa.id)
        embed = post.call_args.kwargs["json"]["embeds"][0]
        self.assertEqual(embed["title"], "Nieuwe Leave of Absence")
        self.assertEqual(embed["fields"][0]["name"], "Speler")

    @patch("aa_loa.tasks.requests.post")
    def test_webhook_ignores_the_language_of_the_trigger(self, post, *_signals):
        LOAConfig.objects.create(
            discord_webhook_url="https://discord.test/hook", discord_language="en"
        )
        loa = self._loa()
        with translation.override("nl"):
            send_loa_webhook(loa.id)
        self.assertEqual(
            post.call_args.kwargs["json"]["embeds"][0]["title"], "New Leave of Absence"
        )
