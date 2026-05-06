from django.db import transaction
from rest_framework import serializers

from .models import (
    LibrarySection,
    Shelf,
    Author,
    Book,
    BookAuthor,
    BookCopy,
    BookFile,
    Loan,
    MemberProfile,
)


class LibrarySectionSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibrarySection
        fields = ["id", "name", "slug", "parent"]


class BookSlimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "slug", "archive_number"]


class ShelfSerializer(serializers.ModelSerializer):
    books_count = serializers.IntegerField(read_only=True)
    copies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Shelf
        fields = [
            "id",
            "code",
            "name",
            "position",
            "description",
            "is_active",
            "books_count",
            "copies_count",
            "created_at",
            "updated_at",
        ]


class AuthorSerializer(serializers.ModelSerializer):
    books_count = serializers.IntegerField(read_only=True)
    books = BookSlimSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = [
            "id",
            "full_name",
            "biography",
            "image",
            "birth_date",
            "death_date",
            "country",
            "is_active",
            "books_count",
            "books",
            "created_at",
            "updated_at",
        ]


class BookAuthorSerializer(serializers.ModelSerializer):
    author_detail = AuthorSerializer(source="author", read_only=True)

    class Meta:
        model = BookAuthor
        fields = ["id", "author", "author_detail", "order", "is_primary", "created_at", "updated_at"]


class BookCopySerializer(serializers.ModelSerializer):
    book_detail = BookSlimSerializer(source="book", read_only=True)
    shelf_detail = ShelfSerializer(source="shelf", read_only=True)

    class Meta:
        model = BookCopy
        fields = [
            "id",
            "book",
            "book_detail",
            "copy_number",
            "status",
            "shelf",
            "shelf_detail",
            "notes",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "book": {"required": False},
        }


class BookFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookFile
        fields = [
            "id",
            "book",
            "title",
            "file",
            "file_type",
            "description",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "book": {"required": False},
        }


class BookSerializer(serializers.ModelSerializer):
    section_detail = LibrarySectionSlimSerializer(source="section", read_only=True)
    shelf_detail = ShelfSerializer(source="shelf", read_only=True)
    authors_detail = AuthorSerializer(source="authors", many=True, read_only=True)
    book_authors_detail = BookAuthorSerializer(source="book_authors", many=True, read_only=True)
    copies_detail = BookCopySerializer(source="copies", many=True, read_only=True)
    files_detail = BookFileSerializer(source="files", many=True, read_only=True)

    copies_count = serializers.IntegerField(read_only=True)
    available_copies_count = serializers.IntegerField(read_only=True)
    files_count = serializers.IntegerField(read_only=True)

    authors = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Author.objects.all(),
        required=False,
    )
    copies = BookCopySerializer(many=True, required=False, write_only=True)
    files = BookFileSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "subtitle",
            "slug",
            "section",
            "section_detail",
            "shelf",
            "shelf_detail",
            "authors",
            "authors_detail",
            "book_authors_detail",
            "description",
            "isbn",
            "archive_number",
            "publisher",
            "publication_year",
            "language",
            "pages",
            "cover_image",
            "is_active",
            "copies",
            "copies_detail",
            "files",
            "files_detail",
            "copies_count",
            "available_copies_count",
            "files_count",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "slug": {"required": False},
        }

    def create(self, validated_data):
        authors = validated_data.pop("authors", [])
        copies_data = validated_data.pop("copies", [])
        files_data = validated_data.pop("files", [])

        with transaction.atomic():
            book = Book.objects.create(**validated_data)

            if authors:
                book_authors = []
                for index, author in enumerate(authors, start=1):
                    book_authors.append(
                        BookAuthor(
                            book=book,
                            author=author,
                            order=index,
                            is_primary=(index == 1),
                        )
                    )
                BookAuthor.objects.bulk_create(book_authors)

            for copy_data in copies_data:
                BookCopy.objects.create(book=book, **copy_data)

            for file_data in files_data:
                BookFile.objects.create(book=book, **file_data)

        return book

    def update(self, instance, validated_data):
        authors = validated_data.pop("authors", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        with transaction.atomic():
            instance.save()

            if authors is not None:
                BookAuthor.objects.filter(book=instance).delete()
                book_authors = []
                for index, author in enumerate(authors, start=1):
                    book_authors.append(
                        BookAuthor(
                            book=instance,
                            author=author,
                            order=index,
                            is_primary=(index == 1),
                        )
                    )
                BookAuthor.objects.bulk_create(book_authors)

        return instance


class LibrarySectionSerializer(serializers.ModelSerializer):
    parent_detail = LibrarySectionSlimSerializer(source="parent", read_only=True)
    children = LibrarySectionSlimSerializer(many=True, read_only=True)
    books = BookSlimSerializer(many=True, read_only=True)
    books_count = serializers.IntegerField(read_only=True)
    children_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = LibrarySection
        fields = [
            "id",
            "name",
            "parent",
            "parent_detail",
            "description",
            "slug",
            "is_active",
            "children",
            "books",
            "books_count",
            "children_count",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "slug": {"required": False},
        }


class LoanSerializer(serializers.ModelSerializer):
    copy_detail = BookCopySerializer(source="copy", read_only=True)
    borrower_detail = serializers.StringRelatedField(source="borrower", read_only=True)
    handled_by_detail = serializers.StringRelatedField(source="handled_by", read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "copy",
            "copy_detail",
            "borrower",
            "borrower_detail",
            "handled_by",
            "handled_by_detail",
            "loan_date",
            "due_date",
            "returned_at",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["loan_date"]

    def create(self, validated_data):
        loan = super().create(validated_data)
        copy = loan.copy
        copy.status = BookCopy.Status.BORROWED
        copy.save(update_fields=["status", "updated_at"])
        return loan

    def update(self, instance, validated_data):
        previous_status = instance.status
        loan = super().update(instance, validated_data)

        if previous_status != Loan.Status.RETURNED and loan.status == Loan.Status.RETURNED:
            loan.returned_at = loan.returned_at or loan.updated_at.date()
            loan.save(update_fields=["returned_at", "updated_at"])
            loan.copy.status = BookCopy.Status.AVAILABLE
            loan.copy.save(update_fields=["status", "updated_at"])

        return loan


class MemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = [
            "id",
            "user",
            "card_number",
            "phone",
            "address",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]