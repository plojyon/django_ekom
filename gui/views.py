from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from backend.models import Submission, Professor, Year, Type, AuthCode
from .forms import UploadFileForm, FilterForm, AuthcodeGeneratorForm
from django.db.models import Q
from django.contrib.auth import authenticate


def SubmissionsList(request):
    template_name = "gui/submissions_list.html"
    data = {}
    data["submissions"] = Submission.objects.all()
    data["filters"] = FilterForm(request.GET)
    filters = list(request.GET.lists())
    for filter in filters:
        key = filter[0]
        values = filter[1]
        q = Q()
        for value in values:
            if key == "year":
                q |= Q(year=Year(int(value)))
            elif key == "type":
                q |= Q(type=Type(int(value)))
            elif key == "professor":
                q |= Q(professor__id=value)
            elif key == "subject":
                q |= Q(subject__id=value)
            elif key == "tags":
                q |= Q(tags__id=value)
        data["submissions"] = data["submissions"].filter(q)
    return render(request, template_name, data)


class ProfessorsList(generic.ListView):
    template_name = "gui/prof_list.html"
    context_object_name = "professors"
    model = Professor


class ProfessorsDetail(generic.DetailView):
    model = Professor
    template_name = "gui/prof_detail.html"
    context_object_name = "professor"


def Upload(request):
    error = ""
    form = UploadFileForm()
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if not AuthCode.is_valid(form.cleaned_data["authcode"]):
                    raise ValueError("Napacna avtorizacijska koda.")
                sub = Submission.from_form_data(form.cleaned_data)
                AuthCode.use(sub, form.cleaned_data["authcode"])
                return HttpResponse("Upload successful. <a href='../..'>Nazaj</a>")
            except Exception as e:
                error = "Error: " + str(e)
        else:
            error = "Invalid form data"
    return render(request, "gui/upload.html", {"form": form, "error": error})


def AuthcodeGenerator(request):
    error = ""
    success = ""
    form = AuthcodeGeneratorForm()
    if request.method == "POST":
        form = AuthcodeGeneratorForm(request.POST)
        if not form.is_valid():
            error = "Invalid form data"
        else:
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                code = AuthCode.from_form_data(form.cleaned_data).code
                success = "Uspeh! Koda: " + code
            else:
                error = "Invalid credentials"

    return render(
        request,
        "gui/authcode_generator.html",
        {"form": form, "error": error, "success": success},
    )
