from rest_framework import permissions, viewsets
from .models import Rule, Field, FieldMapper
from .serializers import RuleSerializer, FieldSerializer, FieldMapperSerializer


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAuthenticated]


class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [permissions.IsAuthenticated]


class FieldMapperViewSet(viewsets.ModelViewSet):
    queryset = FieldMapper.objects.all()
    serializer_class = FieldMapperSerializer
    permission_classes = [permissions.IsAuthenticated]
