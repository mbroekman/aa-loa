from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import LeaveOfAbsence


class PlayerLOAForm(forms.ModelForm):
    class Meta:
        model = LeaveOfAbsence
        fields = ["start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date for HTML5 date pickers to today
        today_str = timezone.localdate().strftime("%Y-%m-%d")
        self.fields['start_date'].widget.attrs.update({'min': today_str})
        self.fields['end_date'].widget.attrs.update({'min': today_str})

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date and start_date < timezone.localdate():
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data


class DirectorLOAForm(PlayerLOAForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Player",
    )

    class Meta(PlayerLOAForm.Meta):
        fields = ["user", "start_date", "end_date", "reason"]
