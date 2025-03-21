from django.urls import path
from .views import ChatAPIView, MedicalReportAPIView, HospitalSearchAPIView, NewsAPIView, ClusterAPIView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat_api"),
    path("upload-report/", MedicalReportAPIView.as_view(), name="upload_report_api"),
    path('get-hospitals/', HospitalSearchAPIView.as_view(), name='get_hospitals_api'),
    path('get-news/', NewsAPIView.as_view(), name='get_news_api'),
    path('get-outbreaks/', ClusterAPIView.as_view(), name='get_outbreaks_api'),
]
