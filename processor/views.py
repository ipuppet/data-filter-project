from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .processor import FileConverter, Matcher, TableStructure
from .models import File
from .forms import FileForm


class FilesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fileList = File.objects.all().values("id", "display_name")
        return Response({"files": fileList}, status=status.HTTP_200_OK)

    def post(self, request):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.display_name = file_instance.file.name
            file_instance.save()
            return Response(
                {"id": file_instance.id, "display_name": file_instance.display_name},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


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
                "tables": TableStructure(file_instance).fetch(),
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
                "Invalid pagination parameters", status=status.HTTP_400_BAD_REQUEST
            )

        matcher = Matcher(file_instance)
        return Response(
            matcher.fetch_all_data(page_number, items_per_page),
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        id = request.data.get("id")
        file_instance = get_object_or_404(File, id=id)

        matcher = Matcher(file_instance)
        matcher.set_table(request.data.get("table"))
        return Response(
            matcher.fetch(),
            status=status.HTTP_200_OK,
        )
