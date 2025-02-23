from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from rules.models import Rule
from .processor import FileConverter, DBStructure
from .matcher import Matcher
from .models import File
from .serializers import FileSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all().order_by("-uploaded_at")
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProcessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        file_instance = get_object_or_404(File, id=file_id)

        try:
            FileConverter(file_instance).convert()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class MetadataView(APIView):
    def get(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        file_instance = get_object_or_404(File, id=file_id)
        return Response(
            {
                "id": file_instance.id,
                "display_name": file_instance.display_name,
                "uploaded_at": file_instance.uploaded_at,
                "tables": DBStructure(file_instance).fetch(),
            },
            status=status.HTTP_200_OK,
        )


class MatchDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("file_id")
        file_instance = get_object_or_404(File, id=file_id)
        table_name = request.data.get("table")
        rule_id = request.data.get("rule_id")

        matcher = Matcher()
        matcher.set_file(file_instance).set_rule(rule_id).set_table(table_name).fetch()
        return Response(
            {"path": matcher.url_path, "df": matcher.df.to_json(orient="columns")},
            status=status.HTTP_200_OK,
        )


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class HomeView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["files"] = File.objects.all().order_by("-uploaded_at")
        context["rules"] = Rule.objects.all()
        return context
