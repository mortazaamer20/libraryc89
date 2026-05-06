from django.contrib import admin
from django.http import FileResponse, HttpResponse
from django.template.response import TemplateResponse
from django.utils import timezone

from .forms import ReportPeriodForm
from .services import build_report_data, export_excel_report, export_pdf_report


def library_reports_view(request):
    form = ReportPeriodForm(request.GET or None)
    data = None

    if form.is_valid():
        cleaned = form.cleaned_data
        data = build_report_data(
            period=cleaned["period"],
            date_from=cleaned.get("date_from"),
            date_to=cleaned.get("date_to"),
        )

        output = cleaned["output"]

        if output == "pdf":
            font_path = getattr(
                __import__("django.conf").conf.settings,
                "REPORTS_PDF_FONT_PATH",
                None,
            )
            pdf_bytes = export_pdf_report(data, font_path=font_path)
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="library-report.pdf"'
            return response

        if output == "xlsx":
            excel_bytes = export_excel_report(data)
            response = HttpResponse(
                excel_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="library-report.xlsx"'
            return response

    else:
        cleaned = {}
        data = build_report_data("month")

    context = {
        **admin.site.each_context(request),
        "title": "تقارير المكتبة",
        "form": form,
        "data": data,
        "now": timezone.localdate(),
    }
    return TemplateResponse(request, "admin/library_reports.html", context)