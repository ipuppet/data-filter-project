from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = router.urls + [
    path("upload/", views.UploadFile.as_view()),
]
