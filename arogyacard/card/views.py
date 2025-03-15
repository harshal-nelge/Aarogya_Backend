import os
import json
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import get_medical_response  # Chatbot logic
from .serializers import DocumentUploadSerializer
from .report import process_medical_report  # Google Gemini API processing

class ChatAPIView(APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        hid = data.get("hid")
        query = data.get("query")

        if not hid or not query:
            return Response({"error": "Missing hid or query"}, status=status.HTTP_400_BAD_REQUEST)

        response = get_medical_response(hid, query)

        return Response({"hid": hid, "query": query, "response": response}, status=status.HTTP_200_OK)

class MedicalReportAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = DocumentUploadSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = serializer.validated_data['document']

            # Save file locally
            file_path = default_storage.path(default_storage.save(pdf_file.name, pdf_file))

            # Process with Google Gemini API
            response_data = process_medical_report(file_path)

            # Delete file after processing
            if os.path.exists(file_path):
                os.remove(file_path)

            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
