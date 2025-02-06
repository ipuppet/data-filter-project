from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import File
from .forms import FileForm


class UploadFile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fileList = File.objects.all().values("name", "file")
        return Response({"files": fileList}, status=status.HTTP_200_OK)

    def post(self, request):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.name = request.data.get("name", "")
            file_instance.save()
            return Response(
                {"message": "File uploaded successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
