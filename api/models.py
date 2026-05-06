# library/models.py
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التعديل"), auto_now=True)

    class Meta:
        abstract = True


class LibrarySection(TimeStampedModel):
    """
    الأقسام الرئيسية والفرعية للمكتبة.
    parent = Null => قسم رئيسي
    parent != Null => قسم فرعي
    """
    name = models.CharField(_("اسم القسم"), max_length=150)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("القسم الأب"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(_("وصف القسم"), blank=True)
    slug = models.SlugField(_("الرابط المختصر"), max_length=180, unique=True)
    is_active = models.BooleanField(_("نشط"), default=True)

    class Meta:
        verbose_name = _("قسم")
        verbose_name_plural = _("الأقسام")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class Shelf(TimeStampedModel):
    class PositionChoices(models.TextChoices):
        TOP = "top", _("أعلى")
        BOTTOM = "bottom", _("أسفل")
        SIDE = "side", _("جانبي")
        FRONT = "front", _("أمامي")
        BACK = "back", _("خلفي")
        CUSTOM = "custom", _("مخصص")

    code = models.CharField(_("رمز الرف"), max_length=50, unique=True)
    name = models.CharField(_("اسم الرف"), max_length=150)
    position = models.CharField(
        _("مكان الرف"),
        max_length=20,
        choices=PositionChoices.choices,
        default=PositionChoices.CUSTOM,
    )
    description = models.TextField(_("وصف الرف"), blank=True)
    is_active = models.BooleanField(_("نشط"), default=True)

    class Meta:
        verbose_name = _("رف")
        verbose_name_plural = _("الأرفف")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Author(TimeStampedModel):
    full_name = models.CharField(_("اسم المؤلف"), max_length=200)
    biography = models.TextField(_("نبذة عن المؤلف"), blank=True)
    image = models.ImageField(_("صورة المؤلف"), upload_to="authors/", blank=True, null=True)
    birth_date = models.DateField(_("تاريخ الميلاد"), blank=True, null=True)
    death_date = models.DateField(_("تاريخ الوفاة"), blank=True, null=True)
    country = models.CharField(_("البلد"), max_length=120, blank=True)
    is_active = models.BooleanField(_("نشط"), default=True)

    class Meta:
        verbose_name = _("مؤلف")
        verbose_name_plural = _("المؤلفون")
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["full_name"]),
        ]

    def __str__(self):
        return self.full_name

 


class Book(TimeStampedModel):
    title = models.CharField(_("عنوان الكتاب"), max_length=255)
    subtitle = models.CharField(_("العنوان الفرعي"), max_length=255, blank=True)
    slug = models.SlugField(_("الرابط المختصر"), max_length=280, unique=True)

    section = models.ForeignKey(
        LibrarySection,
        verbose_name=_("القسم"),
        on_delete=models.PROTECT,
        related_name="books",
    )

    shelf = models.ForeignKey(
        Shelf,
        verbose_name=_("الرف"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )

    authors = models.ManyToManyField(
        Author,
        verbose_name=_("المؤلفون"),
        through="BookAuthor",
        related_name="books",
    )

    description = models.TextField(_("نبذة عن الكتاب"), blank=True)
    isbn = models.CharField(_("ISBN"), max_length=20, blank=True, db_index=True)
    archive_number = models.CharField(_("رقم الأرشفة"), max_length=50, unique=True)
    publisher = models.CharField(_("الناشر"), max_length=200, blank=True)
    publication_year = models.PositiveIntegerField(_("سنة النشر"), blank=True, null=True)
    language = models.CharField(_("اللغة"), max_length=60, blank=True)
    pages = models.PositiveIntegerField(_("عدد الصفحات"), blank=True, null=True)
    cover_image = models.ImageField(_("صورة الغلاف"), upload_to="books/covers/", blank=True, null=True)
    is_active = models.BooleanField(_("نشط"), default=True)

    class Meta:
        verbose_name = _("كتاب")
        verbose_name_plural = _("الكتب")
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["isbn"]),
            models.Index(fields=["archive_number"]),
        ]

    def __str__(self):
        return self.title


    @property
    def available_copies_count(self):
        return self.copies.filter(status=BookCopy.Status.AVAILABLE).count()


class BookAuthor(TimeStampedModel):
    """
    جدول وسيط اختياري إذا تريد:
    - ترتيب المؤلفين
    - تحديد المؤلف الرئيسي
    - أي ملاحظات إضافية
    """
    book = models.ForeignKey(Book, verbose_name=_("الكتاب"), on_delete=models.CASCADE, related_name="book_authors")
    author = models.ForeignKey(Author, verbose_name=_("المؤلف"), on_delete=models.CASCADE, related_name="author_books")
    order = models.PositiveSmallIntegerField(_("ترتيب العرض"), default=1)
    is_primary = models.BooleanField(_("مؤلف رئيسي"), default=False)

    class Meta:
        verbose_name = _("مؤلف الكتاب")
        verbose_name_plural = _("مؤلفو الكتب")
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(fields=["book", "author"], name="unique_book_author"),
            models.UniqueConstraint(
                fields=["book"],
                condition=Q(is_primary=True),
                name="unique_primary_author_per_book",
            ),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.author.full_name}"


class BookCopy(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE = "available", _("موجود")
        BORROWED = "borrowed", _("تم اعارته")
        MISSING = "missing", _("غير موجود")
        DAMAGED = "damaged", _("متضرر")
        RESERVED = "reserved", _("محجوز")

    book = models.ForeignKey(
        Book,
        verbose_name=_("الكتاب"),
        on_delete=models.CASCADE,
        related_name="copies",
    )
    copy_number = models.CharField(_("رقم النسخة"), max_length=50)
    status = models.CharField(
        _("حالة النسخة"),
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )
    shelf = models.ForeignKey(
        Shelf,
        verbose_name=_("الرف"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="copies",
    )
    notes = models.TextField(_("ملاحظات"), blank=True)

    class Meta:
        verbose_name = _("نسخة كتاب")
        verbose_name_plural = _("نسخ الكتب")
        ordering = ["book__title", "copy_number"]
        constraints = [
            models.UniqueConstraint(fields=["book", "copy_number"], name="unique_copy_number_per_book"),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["copy_number"]),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.copy_number}"


class BookFile(TimeStampedModel):
    class FileTypeChoices(models.TextChoices):
        PDF = "pdf", _("PDF")
        IMAGE = "image", _("صورة")
        DOC = "doc", _("مستند")
        OTHER = "other", _("أخرى")

    book = models.ForeignKey(
        Book,
        verbose_name=_("الكتاب"),
        on_delete=models.CASCADE,
        related_name="files",
    )
    title = models.CharField(_("عنوان الملف"), max_length=200)
    file = models.FileField(_("الملف"), upload_to="books/files/")
    file_type = models.CharField(
        _("نوع الملف"),
        max_length=20,
        choices=FileTypeChoices.choices,
        default=FileTypeChoices.OTHER,
    )
    description = models.TextField(_("وصف الملف"), blank=True)

    class Meta:
        verbose_name = _("ملف كتاب")
        verbose_name_plural = _("ملفات الكتب")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.book.title} - {self.title}"


class Loan(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", _("سارية")
        RETURNED = "returned", _("مُعادة")
        OVERDUE = "overdue", _("متأخرة")
        CANCELED = "canceled", _("ملغاة")

    copy = models.ForeignKey(
        BookCopy,
        verbose_name=_("نسخة الكتاب"),
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("المستعير"),
        on_delete=models.PROTECT,
        related_name="book_loans",
    )
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("الموظف المسؤول"),
        on_delete=models.PROTECT,
        related_name="handled_loans",
    )
    loan_date = models.DateField(_("تاريخ الإعارة"), auto_now_add=True)
    due_date = models.DateField(_("تاريخ الإرجاع المتوقع"))
    returned_at = models.DateField(_("تاريخ الإرجاع"), blank=True, null=True)
    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    notes = models.TextField(_("ملاحظات"), blank=True)

    class Meta:
        verbose_name = _("إعارة")
        verbose_name_plural = _("الإعارات")
        ordering = ["-loan_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["copy"],
                condition=Q(status="active"),
                name="unique_active_loan_per_copy",
            )
        ]

    def __str__(self):
        return f"{self.copy} - {self.borrower}"


class MemberProfile(TimeStampedModel):
    """
    اختياري إذا تريد فصل بيانات الأعضاء عن User.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("المستخدم"),
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    card_number = models.CharField(_("رقم البطاقة"), max_length=50, unique=True)
    phone = models.CharField(_("رقم الهاتف"), max_length=30, blank=True)
    address = models.CharField(_("العنوان"), max_length=255, blank=True)
    notes = models.TextField(_("ملاحظات"), blank=True)
    is_active = models.BooleanField(_("نشط"), default=True)

    class Meta:
        verbose_name = _("عضو")
        verbose_name_plural = _("الأعضاء")
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user} - {self.card_number}"