from django.urls import path
from . import views

urlpatterns = [
    path("", views.SubmissionsList, name="submissions_list"),
    path("upload/", views.Upload, name="upload"),
    path("professors/", views.ProfessorsList.as_view(), name="prof_list"),
    path("professors/<int:pk>/", views.ProfessorsDetail.as_view(), name="prof_detail"),
    path("authcode/", views.AuthcodeGenerator, name="authcode_generator"),
]
