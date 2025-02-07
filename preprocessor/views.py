from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .file_processor import FileProcessor
from .models import File
from .forms import FileForm


class UploadFile(APIView):
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


class ProcessFile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_id = request.data.get("id")
        file_instance = File.objects.get(id=file_id)
        try:
            FileProcessor(file_instance).process()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
