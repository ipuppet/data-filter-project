from rest_framework import serializers

from .models import File


class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(
        max_length=None, use_url=True  # 设置为 True 以返回文件的 URL，否则返回文件名
    )

    class Meta:
        model = File
        fields = ["id", "display_name", "file", "uploaded_at"]
        read_only_fields = ["id", "display_name", "uploaded_at"]

    def create(self, validated_data):
        validated_data["display_name"] = validated_data["file"].name
        return super().create(validated_data)
