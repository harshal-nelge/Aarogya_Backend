from rest_framework import serializers

class DocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField()