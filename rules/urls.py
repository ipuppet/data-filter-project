from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"rules", views.RuleViewSet)
router.register(r"fields", views.FieldViewSet)
router.register(r"field-mappers", views.FieldMapperViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
