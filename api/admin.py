from django.contrib import admin
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


@admin.register(LibrarySection)
class LibrarySectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "is_active", "created_at")
    search_fields = ("name", "description", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Shelf)
class ShelfAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "position", "is_active")
    search_fields = ("code", "name")
    list_filter = ("position", "is_active")
    ordering = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "country", "is_active", "created_at")
    search_fields = ("full_name", "biography", "country")
    list_filter = ("is_active", "country")
    ordering = ("full_name",)


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1


class BookFileInline(admin.TabularInline):
    model = BookFile
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "section", "shelf", "isbn", "archive_number", "is_active")
    search_fields = ("title", "subtitle", "isbn", "archive_number", "description")
    list_filter = ("is_active", "section", "shelf", "publication_year")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [BookAuthorInline, BookCopyInline, BookFileInline]
    ordering = ("title",)


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "author", "order", "is_primary")
    search_fields = ("book__title", "author__full_name")
    list_filter = ("is_primary",)
    ordering = ("order",)


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "copy_number", "status", "shelf")
    search_fields = ("book__title", "copy_number")
    list_filter = ("status", "shelf")
    ordering = ("book__title", "copy_number")


@admin.register(BookFile)
class BookFileAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "title", "file_type", "created_at")
    search_fields = ("book__title", "title", "description")
    list_filter = ("file_type",)
    ordering = ("-created_at",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("id", "copy", "borrower", "handled_by", "status", "loan_date", "due_date")
    search_fields = ("copy__book__title", "borrower__username", "borrower__email")
    list_filter = ("status", "loan_date", "due_date")
    ordering = ("-loan_date",)


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "card_number", "phone", "is_active")
    search_fields = ("user__username", "user__email", "card_number", "phone")
    list_filter = ("is_active",)
    ordering = ("user__username",)