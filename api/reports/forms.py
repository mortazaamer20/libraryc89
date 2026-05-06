from django import forms


class ReportPeriodForm(forms.Form):
    PERIOD_CHOICES = (
        ("today", "اليوم"),
        ("week", "الأسبوع"),
        ("month", "الشهر"),
        ("all", "الكلي"),
        ("custom", "مخصص"),
    )

    OUTPUT_CHOICES = (
        ("html", "عرض داخل المتصفح"),
        ("pdf", "PDF"),
        ("xlsx", "Excel"),
    )

    period = forms.ChoiceField(
        label="الفترة",
        choices=PERIOD_CHOICES,
        initial="month",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    date_from = forms.DateField(
        label="من تاريخ",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_to = forms.DateField(
        label="إلى تاريخ",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    output = forms.ChoiceField(
        label="نوع التصدير",
        choices=OUTPUT_CHOICES,
        initial="html",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean(self):
        cleaned = super().clean()
        period = cleaned.get("period")
        date_from = cleaned.get("date_from")
        date_to = cleaned.get("date_to")

        if period == "custom":
            if not date_from or not date_to:
                raise forms.ValidationError("لازم تحدد من تاريخ وإلى تاريخ عند اختيار الفترة المخصصة.")
            if date_from > date_to:
                raise forms.ValidationError("تاريخ البداية لا يمكن يكون بعد تاريخ النهاية.")

        return cleaned