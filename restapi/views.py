from rest_framework import viewsets, generics, permissions, mixins
from rest_framework.response import Response
from backend.models import Submission, AuthCode
from .serializers import SubmissionSerializer, AuthCodeSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    """API endpoint that lists all submissions."""

    queryset = Submission.objects.all().order_by("-pk")
    serializer_class = SubmissionSerializer


class AuthcodeViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """API endpoint that lists all authcodes."""

    queryset = AuthCode.objects.all().order_by("-pk")
    serializer_class = AuthCodeSerializer


from django.shortcuts import render


def index(request):
    return render(request, "restapi/index.html", {"form": SubmissionSerializer})
