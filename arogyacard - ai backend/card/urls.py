from django.urls import path
from .views import ChatAPIView, MedicalReportAPIView, HospitalSearchAPIView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat_api"),
    path("upload-report/", MedicalReportAPIView.as_view(), name="upload_report_api"),
    path('get-hospitals/', HospitalSearchAPIView.as_view(), name='get_hospitals_api'),
]
