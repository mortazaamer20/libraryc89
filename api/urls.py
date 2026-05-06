from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LibrarySectionViewSet,
    ShelfViewSet,
    AuthorViewSet,
    BookViewSet,
    BookCopyViewSet,
    BookFileViewSet,
    LoanViewSet,
    MemberProfileViewSet,
    DashboardAPIView,
)

router = DefaultRouter()
router.register(r"sections", LibrarySectionViewSet, basename="sections")
router.register(r"shelves", ShelfViewSet, basename="shelves")
router.register(r"authors", AuthorViewSet, basename="authors")
router.register(r"books", BookViewSet, basename="books")
router.register(r"copies", BookCopyViewSet, basename="copies")
router.register(r"files", BookFileViewSet, basename="files")
router.register(r"loans", LoanViewSet, basename="loans")
router.register(r"members", MemberProfileViewSet, basename="members")

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
    path("", include(router.urls)),
]