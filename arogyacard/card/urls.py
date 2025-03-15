from django.urls import path
from .views import MedicalReportAPIView

urlpatterns = [
    path('upload-report/', MedicalReportAPIView.as_view(), name='upload-report'),
]