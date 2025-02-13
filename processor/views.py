from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
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

    def post(self, request):
        id = request.data.get("id")
        file_instance = get_object_or_404(File, id=id)

        try:
            FileConverter(file_instance).convert()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class MetadataView(APIView):
    def get(self, request, *args, **kwargs):
        id = kwargs.get("id")
        file_instance = get_object_or_404(File, id=id)
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

    def get(self, request, *args, **kwargs):
        id = kwargs.get("id")
        file_instance = get_object_or_404(File, id=id)

        try:
            page_number = int(request.query_params.get("page_number", 1))
            items_per_page = int(request.query_params.get("items_per_page", 10))
        except ValueError:
            return Response(
                _("Invalid pagination parameters"), status=status.HTTP_400_BAD_REQUEST
            )

        matcher = Matcher(file_instance)
        return Response(
            matcher.fetch_all_data(page_number, items_per_page),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        file_id = request.data.get("file_id")
        file_instance = get_object_or_404(File, id=file_id)
        table_name = request.data.get("table")
        rule_id = request.data.get("rule_id")

        matcher = Matcher()
        matcher.set_file(file_instance).set_rule(rule_id).set_table(table_name)
        return Response(
            {"path": matcher.fetch()},
            status=status.HTTP_200_OK,
        )
