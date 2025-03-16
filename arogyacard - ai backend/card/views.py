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
from .models import ChatHistory

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


from .utils import extract_disease_from_response, get_nearby_hospitals

class HospitalSearchAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """Extracts disease from chatbot response and fetches nearby hospitals based on hid."""
        data = json.loads(request.body)
        hid = data.get("hid", "")
        location = data.get("location", "")

        if not hid or not location:
            return Response({"error": "HID and location are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve conversation history from the database
        try:
            chat_history = ChatHistory.objects.get(hid=hid)
            response_text = "\n".join(chat_history.conversation.values())  # Combine all responses
        except ChatHistory.DoesNotExist:
            return Response({"error": "Chat history not found for the given HID."}, status=status.HTTP_404_NOT_FOUND)

        # Extract disease from chatbot response
        disease = extract_disease_from_response(response_text)
        
        if disease == "Unknown":
            return Response({"error": "Could not extract a disease from the response."}, status=status.HTTP_400_BAD_REQUEST)

        # Get nearby hospitals based on the extracted disease and location
        hospitals = get_nearby_hospitals(disease, location)

        return Response({
            "disease": disease,
            "location": location,
            "hospitals": hospitals
        }, status=status.HTTP_200_OK)

