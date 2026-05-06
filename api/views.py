from django.db.models import Count, Q
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

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

from .serializers import (
    LibrarySectionSerializer,
    ShelfSerializer,
    AuthorSerializer,
    BookSerializer,
    BookCopySerializer,
    BookFileSerializer,
    LoanSerializer,
    MemberProfileSerializer,
)

from .filters import (
    LibrarySectionFilter,
    ShelfFilter,
    AuthorFilter,
    BookFilter,
    BookCopyFilter,
    BookFileFilter,
    LoanFilter,
    MemberProfileFilter,
)


class BaseAuthenticatedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class LibrarySectionViewSet(BaseAuthenticatedViewSet):
    serializer_class = LibrarySectionSerializer
    filterset_class = LibrarySectionFilter
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        return (
            LibrarySection.objects.select_related("parent")
            .prefetch_related("children", "books")
            .annotate(
                books_count=Count("books", distinct=True),
                children_count=Count("children", distinct=True),
            )
        )

    @action(detail=True, methods=["get"])
    def books(self, request, pk=None):
        section = self.get_object()
        qs = (
            Book.objects.select_related("section", "shelf")
            .prefetch_related("authors", "copies", "files")
            .filter(section=section)
            .annotate(
                copies_count=Count("copies", distinct=True),
                available_copies_count=Count(
                    "copies",
                    filter=Q(copies__status=BookCopy.Status.AVAILABLE),
                    distinct=True,
                ),
                files_count=Count("files", distinct=True),
            )
        )
        serializer = BookSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class ShelfViewSet(BaseAuthenticatedViewSet):
    serializer_class = ShelfSerializer
    filterset_class = ShelfFilter
    search_fields = ["code", "name", "description"]
    ordering_fields = ["name", "code", "created_at"]

    def get_queryset(self):
        return (
            Shelf.objects.prefetch_related("books", "copies")
            .annotate(
                books_count=Count("books", distinct=True),
                copies_count=Count("copies", distinct=True),
            )
        )


class AuthorViewSet(BaseAuthenticatedViewSet):
    serializer_class = AuthorSerializer
    filterset_class = AuthorFilter
    search_fields = ["full_name", "biography", "country"]
    ordering_fields = ["full_name", "created_at"]

    def get_queryset(self):
        return (
            Author.objects.prefetch_related("books")
            .annotate(
                books_count=Count("books", distinct=True),
            )
        )

    @action(detail=True, methods=["get"])
    def books(self, request, pk=None):
        author = self.get_object()
        qs = (
            Book.objects.select_related("section", "shelf")
            .prefetch_related("authors", "copies", "files")
            .filter(authors=author)
            .annotate(
                copies_count=Count("copies", distinct=True),
                available_copies_count=Count(
                    "copies",
                    filter=Q(copies__status=BookCopy.Status.AVAILABLE),
                    distinct=True,
                ),
                files_count=Count("files", distinct=True),
            )
            .distinct()
        )
        serializer = BookSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class BookViewSet(BaseAuthenticatedViewSet):
    serializer_class = BookSerializer
    filterset_class = BookFilter
    search_fields = [
        "title",
        "subtitle",
        "isbn",
        "archive_number",
        "description",
        "authors__full_name",
        "section__name",
    ]
    ordering_fields = ["title", "publication_year", "created_at", "archive_number"]

    def get_queryset(self):
        return (
            Book.objects.select_related("section", "shelf")
            .prefetch_related("authors", "book_authors__author", "copies", "files")
            .annotate(
                copies_count=Count("copies", distinct=True),
                available_copies_count=Count(
                    "copies",
                    filter=Q(copies__status=BookCopy.Status.AVAILABLE),
                    distinct=True,
                ),
                files_count=Count("files", distinct=True),
            )
            .distinct()
        )


class BookCopyViewSet(BaseAuthenticatedViewSet):
    serializer_class = BookCopySerializer
    filterset_class = BookCopyFilter
    search_fields = ["book__title", "copy_number", "notes"]
    ordering_fields = ["copy_number", "created_at", "status"]

    def get_queryset(self):
        return BookCopy.objects.select_related("book", "book__section", "shelf").prefetch_related("book__authors")

    @action(detail=True, methods=["post"])
    def mark_available(self, request, pk=None):
        copy = self.get_object()
        copy.status = BookCopy.Status.AVAILABLE
        copy.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(copy).data)

    @action(detail=True, methods=["post"])
    def mark_missing(self, request, pk=None):
        copy = self.get_object()
        copy.status = BookCopy.Status.MISSING
        copy.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(copy).data)

    @action(detail=True, methods=["post"])
    def mark_damaged(self, request, pk=None):
        copy = self.get_object()
        copy.status = BookCopy.Status.DAMAGED
        copy.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(copy).data)


class BookFileViewSet(BaseAuthenticatedViewSet):
    serializer_class = BookFileSerializer
    filterset_class = BookFileFilter
    search_fields = ["book__title", "title", "description"]
    ordering_fields = ["created_at", "title", "file_type"]

    def get_queryset(self):
        return BookFile.objects.select_related("book", "book__section")


class LoanViewSet(BaseAuthenticatedViewSet):
    serializer_class = LoanSerializer
    filterset_class = LoanFilter
    search_fields = ["copy__book__title", "borrower__username", "borrower__email", "notes"]
    ordering_fields = ["loan_date", "due_date", "returned_at", "status"]

    def get_queryset(self):
        return Loan.objects.select_related(
            "copy",
            "copy__book",
            "borrower",
            "handled_by",
        )

    @action(detail=True, methods=["post"])
    def return_loan(self, request, pk=None):
        loan = self.get_object()
        loan.status = Loan.Status.RETURNED
        loan.returned_at = timezone.now().date()
        loan.save(update_fields=["status", "returned_at", "updated_at"])

        copy = loan.copy
        copy.status = BookCopy.Status.AVAILABLE
        copy.save(update_fields=["status", "updated_at"])

        return Response(self.get_serializer(loan).data)


class MemberProfileViewSet(BaseAuthenticatedViewSet):
    serializer_class = MemberProfileSerializer
    filterset_class = MemberProfileFilter
    search_fields = ["user__username", "user__email", "card_number", "phone", "address"]
    ordering_fields = ["card_number", "created_at"]

    def get_queryset(self):
        return MemberProfile.objects.select_related("user")


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {
            "sections_count": LibrarySection.objects.filter(is_active=True).count(),
            "authors_count": Author.objects.filter(is_active=True).count(),
            "books_count": Book.objects.filter(is_active=True).count(),
            "copies_total": BookCopy.objects.count(),
            "copies_available": BookCopy.objects.filter(status=BookCopy.Status.AVAILABLE).count(),
            "copies_borrowed": BookCopy.objects.filter(status=BookCopy.Status.BORROWED).count(),
            "copies_missing": BookCopy.objects.filter(status=BookCopy.Status.MISSING).count(),
            "copies_damaged": BookCopy.objects.filter(status=BookCopy.Status.DAMAGED).count(),
            "copies_reserved": BookCopy.objects.filter(status=BookCopy.Status.RESERVED).count(),
            "active_loans": Loan.objects.filter(status=Loan.Status.ACTIVE).count(),
            "overdue_loans": Loan.objects.filter(status=Loan.Status.ACTIVE, due_date__lt=timezone.now().date()).count(),
        }
        return Response(data)