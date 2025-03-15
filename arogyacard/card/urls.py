from django.urls import path
from .views import ChatAPIView, MedicalReportAPIView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat_api"),
    path("upload-report/", MedicalReportAPIView.as_view(), name="upload_report_api"),
]
