from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r"files", views.FileViewSet, basename="file")

urlpatterns = [
    path("", views.HomeView.as_view(), name="home_view"),
    path("api/", include(router.urls)),
    re_path(
        r"^api/process/(?P<file_id>[0-9a-fA-F-]+)/$",
        views.ProcessView.as_view(),
        name="process",
    ),
    re_path(
        r"^api/metadata/(?P<file_id>[0-9a-fA-F-]+)/$", views.MetadataView.as_view()
    ),
    re_path(
        r"^api/match/(?P<file_id>[0-9a-fA-F-]+)?/?$", views.MatchDataView.as_view()
    ),
]
