from django.urls import path
from .views import analyze_career, upload_resume

urlpatterns = [
    path("analyze/", analyze_career),
    path("upload-resume/", upload_resume),
]