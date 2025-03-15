import os
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
# from google import genai
# from google.genai import types
from .serializers import DocumentUploadSerializer
from django.core.files.storage import default_storage
from .report import process_medical_report

class MedicalReportAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['document']

            # Save file locally
            file_path = default_storage.path(default_storage.save(pdf_file.name, pdf_file))

            # Call Google Gemini API
            response_data = process_medical_report(file_path)

            # Delete file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    