import django_filters
from django_filters import rest_framework as filters

from .models import (
    LibrarySection,
    Shelf,
    Author,
    Book,
    BookCopy,
    BookFile,
    Loan,
    MemberProfile,
)


class LibrarySectionFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    slug = filters.CharFilter(field_name="slug", lookup_expr="icontains")
    parent = filters.NumberFilter(field_name="parent_id")
    is_root = filters.BooleanFilter(method="filter_is_root")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = LibrarySection
        fields = ["name", "slug", "parent", "is_root", "is_active"]

    def filter_is_root(self, queryset, name, value):
        if value is True:
            return queryset.filter(parent__isnull=True)
        if value is False:
            return queryset.filter(parent__isnull=False)
        return queryset


class ShelfFilter(filters.FilterSet):
    code = filters.CharFilter(field_name="code", lookup_expr="icontains")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    position = filters.CharFilter(field_name="position")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Shelf
        fields = ["code", "name", "position", "is_active"]


class AuthorFilter(filters.FilterSet):
    full_name = filters.CharFilter(field_name="full_name", lookup_expr="icontains")
    country = filters.CharFilter(field_name="country", lookup_expr="icontains")
    is_active = filters.BooleanFilter(field_name="is_active")
    books_count_min = filters.NumberFilter(method="filter_books_count_min")
    books_count_max = filters.NumberFilter(method="filter_books_count_max")

    class Meta:
        model = Author
        fields = ["full_name", "country", "is_active"]

    def filter_books_count_min(self, queryset, name, value):
        return queryset.filter(books__isnull=False).annotate().filter(books__isnull=False).distinct() if value is None else queryset.annotate().filter(books__isnull=False).distinct()

    def filter_books_count_max(self, queryset, name, value):
        return queryset


class BookFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    subtitle = filters.CharFilter(field_name="subtitle", lookup_expr="icontains")
    isbn = filters.CharFilter(field_name="isbn", lookup_expr="icontains")
    archive_number = filters.CharFilter(field_name="archive_number", lookup_expr="icontains")
    publisher = filters.CharFilter(field_name="publisher", lookup_expr="icontains")
    language = filters.CharFilter(field_name="language", lookup_expr="icontains")

    section = filters.NumberFilter(field_name="section_id")
    section_parent = filters.NumberFilter(field_name="section__parent_id")
    author = filters.NumberFilter(field_name="authors__id")
    shelf = filters.NumberFilter(field_name="shelf_id")

    publication_year_min = filters.NumberFilter(field_name="publication_year", lookup_expr="gte")
    publication_year_max = filters.NumberFilter(field_name="publication_year", lookup_expr="lte")

    status = filters.ChoiceFilter(field_name="copies__status", choices=BookCopy.Status.choices)
    has_files = filters.BooleanFilter(method="filter_has_files")
    has_copies = filters.BooleanFilter(method="filter_has_copies")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Book
        fields = [
            "title",
            "subtitle",
            "isbn",
            "archive_number",
            "publisher",
            "language",
            "section",
            "section_parent",
            "author",
            "shelf",
            "publication_year_min",
            "publication_year_max",
            "status",
            "has_files",
            "has_copies",
            "is_active",
        ]

    def filter_has_files(self, queryset, name, value):
        if value is True:
            return queryset.filter(files__isnull=False).distinct()
        if value is False:
            return queryset.filter(files__isnull=True).distinct()
        return queryset

    def filter_has_copies(self, queryset, name, value):
        if value is True:
            return queryset.filter(copies__isnull=False).distinct()
        if value is False:
            return queryset.filter(copies__isnull=True).distinct()
        return queryset


class BookCopyFilter(filters.FilterSet):
    book = filters.NumberFilter(field_name="book_id")
    book_title = filters.CharFilter(field_name="book__title", lookup_expr="icontains")
    copy_number = filters.CharFilter(field_name="copy_number", lookup_expr="icontains")
    status = filters.ChoiceFilter(field_name="status", choices=BookCopy.Status.choices)
    shelf = filters.NumberFilter(field_name="shelf_id")

    class Meta:
        model = BookCopy
        fields = ["book", "book_title", "copy_number", "status", "shelf"]


class BookFileFilter(filters.FilterSet):
    book = filters.NumberFilter(field_name="book_id")
    book_title = filters.CharFilter(field_name="book__title", lookup_expr="icontains")
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    file_type = filters.CharFilter(field_name="file_type")

    class Meta:
        model = BookFile
        fields = ["book", "book_title", "title", "file_type"]


class LoanFilter(filters.FilterSet):
    borrower = filters.NumberFilter(field_name="borrower_id")
    handled_by = filters.NumberFilter(field_name="handled_by_id")
    copy = filters.NumberFilter(field_name="copy_id")
    status = filters.ChoiceFilter(field_name="status", choices=Loan.Status.choices)
    loan_date = django_filters.DateFromToRangeFilter(field_name="loan_date")
    due_date = django_filters.DateFromToRangeFilter(field_name="due_date")
    returned_at = django_filters.DateFromToRangeFilter(field_name="returned_at")
    overdue = filters.BooleanFilter(method="filter_overdue")

    class Meta:
        model = Loan
        fields = [
            "borrower",
            "handled_by",
            "copy",
            "status",
            "loan_date",
            "due_date",
            "returned_at",
            "overdue",
        ]

    def filter_overdue(self, queryset, name, value):
        from django.utils import timezone

        if value is True:
            return queryset.filter(status=Loan.Status.ACTIVE, due_date__lt=timezone.now().date())
        if value is False:
            return queryset.exclude(status=Loan.Status.ACTIVE, due_date__lt=timezone.now().date())
        return queryset


class MemberProfileFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name="user_id")
    username = filters.CharFilter(field_name="user__username", lookup_expr="icontains")
    email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    card_number = filters.CharFilter(field_name="card_number", lookup_expr="icontains")
    phone = filters.CharFilter(field_name="phone", lookup_expr="icontains")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = MemberProfile
        fields = ["user", "username", "email", "card_number", "phone", "is_active"]