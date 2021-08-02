from django import forms
from backend.models import Type, Year, Professor, Subject, Tag, Extensions

# use this if makemigrations fails (just uncomment, migrate, then comment back again)
"""
class UploadFileForm(forms.Form):
	pass
class FilterForm(forms.Form):
	pass
class AuthcodeGeneratorForm(forms.Form):
	pass
"""


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Datoteka")
    # extension = forms.ChoiceField(choices=[(e, e) for e in Extensions], label='Končnica')
    title = forms.CharField(max_length=150, label="Izviren naslov")
    type = forms.ChoiceField(choices=Type.choices, label="Vrsta")
    author = forms.CharField(max_length=50, label="Avtor (ime ali psevdonim)")
    subject = forms.ChoiceField(
        choices=[(s.id, s.name) for s in Subject.objects.all()], label="Predmet"
    )
    professor = forms.ChoiceField(
        choices=[(p.id, p.full_name) for p in Professor.objects.all()], label="Profesor"
    )
    year = forms.ChoiceField(choices=Year.choices, label="Letnik")
    tags = forms.MultipleChoiceField(
        choices=[(t.id, t.name) for t in Tag.objects.all()],
        label="Oznake (tags)",
        required=False,
    )
    authcode = forms.CharField(max_length=50, label="Avtorizacijska koda")


class FilterForm(forms.Form):
    # construct a custom widget that will reload the page on form change
    my_widget = forms.SelectMultiple(attrs={"onchange": "this.form.submit();"})

    year = forms.MultipleChoiceField(
        choices=Year.choices, label="Letnik", widget=my_widget, required=False
    )
    type = forms.MultipleChoiceField(
        choices=Type.choices, label="Vrsta", widget=my_widget, required=False
    )
    professor = forms.MultipleChoiceField(
        choices=[(p.id, p.full_name) for p in list(Professor.objects.all())],
        label="Profesor",
        widget=my_widget,
        required=False,
    )
    subject = forms.MultipleChoiceField(
        choices=[(s.id, s.name) for s in list(Subject.objects.all())],
        label="Predmet",
        widget=my_widget,
        required=False,
    )
    tags = forms.MultipleChoiceField(
        choices=[(t.id, t.name) for t in Tag.objects.all()],
        label="Oznake (tags)",
        widget=my_widget,
        required=False,
    )


class AuthcodeGeneratorForm(forms.Form):
    username = forms.CharField(max_length=50, label="Uporabnisko ime")
    password = forms.CharField(max_length=50, label="Geslo", widget=forms.PasswordInput)
    purpose = forms.CharField(max_length=200, label="Namen")
