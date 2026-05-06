from django import forms


class AdminReportForm(forms.Form):
    PERIOD_CHOICES = (
        ("day", "يوم"),
        ("week", "أسبوع"),
        ("month", "شهر"),
        ("all", "كلي"),
    )

    FORMAT_CHOICES = (
        ("pdf", "PDF"),
        ("excel", "Excel"),
    )

    GROUP_BY_CHOICES = (
        ("day", "يومي"),
        ("week", "أسبوعي"),
        ("month", "شهري"),
    )

    period = forms.ChoiceField(choices=PERIOD_CHOICES, required=False, initial="month")
    group_by = forms.ChoiceField(choices=GROUP_BY_CHOICES, required=False, initial="month")
    from_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    to_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    format = forms.ChoiceField(choices=FORMAT_CHOICES, required=False, initial="pdf")