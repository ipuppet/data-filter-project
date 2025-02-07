from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = router.urls + [
    path("files/", views.FilesView.as_view()),
    path("process/", views.ProcessView.as_view()),
    re_path(r"^metadata/(?P<id>[0-9a-fA-F-]+)/$", views.MetadataView.as_view()),
    re_path(r"^match/(?P<id>[0-9a-fA-F-]+)?/?$", views.MatchDataView.as_view()),
]
