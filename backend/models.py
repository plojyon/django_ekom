from django.db import models, transaction
from django.utils.translation import gettext_lazy
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Count
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


class Year(models.IntegerChoices):
    OTHER = 0, gettext_lazy("Vsi letniki / drugo")
    FIRST = 1, gettext_lazy("1. letnik")
    SECOND = 2, gettext_lazy("2. letnik")
    THIRD = 3, gettext_lazy("3. letnik")
    FOURTH = 4, gettext_lazy("4. letnik")


class Type(models.IntegerChoices):
    OTHER = 0, gettext_lazy("Drugo")
    NOTES = 1, gettext_lazy("Zapiski")
    EXAM = 2, gettext_lazy("Test")
    PRACTICE = 3, gettext_lazy("Naloge")
    LAB = 4, gettext_lazy("Laboratorijske vaje")


# allowed file extensions (this can absolutely be spoofed)
Extensions = [
    "pdf",
    "docx",
    "txt",
    "odt",
    "png",
    "jpg",
    "gif",
    "jpeg",
    "zip",
    "7z",
    "pub",
]


class TagManager(models.Manager):
    def active(self):
        """Only retrieve actively used tags (those with at least one submission)."""
        return self.annotate(used_count=Count("files")).filter(used_count__gt=0)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    # Related field: .files: ManyToManyField(Submission, related_name="tags")
    objects = TagManager()

    def __str__(self):
        return self.name


class Professor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    subjects = models.ManyToManyField("Subject", related_name="professors")
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return "{first} {last}".format(first=self.first_name, last=self.last_name)


class Subject(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=10, unique=True)
    icon = models.CharField(max_length=20, default="fas fa-graduation-cap")

    def __str__(self):
        return self.name


class AuthCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    authorised_by = models.ForeignKey(
        "Professor", on_delete=models.PROTECT, related_name="auth_codes"
    )
    authorised_datetime = models.DateTimeField(auto_now_add=True)
    used_datetime = models.DateTimeField(null=True, blank=True)
    used_file = models.OneToOneField(
        "Submission",
        on_delete=models.CASCADE,
        related_name="auth_code",
        null=True,
        blank=True,
    )
    purpose = models.CharField(max_length=200)

    def __str__(self):
        status = "unused" if self.used_file is None else self.used_file.title
        return "{code} ({status})".format(code=self.code, status=status)

    @property
    def authoriser(self):
        """Full name of the authorising professor."""
        return self.authorised_by.full_name

    @staticmethod
    def is_valid(code):
        """Checks if the code exists and is unused."""
        ac = AuthCode.objects.filter(code=code)
        if ac.count() != 1:
            return False
        ac = ac[0]
        return ac.used_file is None

    @staticmethod
    def is_available(code):
        """Checks that a code doesn't yet exist."""
        return AuthCode.objects.filter(code=code).count() == 0

    @staticmethod
    def use(submission, code):
        """Uses the code on a submission."""
        if not submission:
            raise ValueError("Cannot use code on null submission")
        ac = AuthCode.objects.get(code=code)
        ac.used_datetime = make_aware(datetime.now())
        ac.used_file = submission
        ac.save()

    @staticmethod
    def from_form_data(data):
        """Create an AuthCode object from data returned by AuthCodeForm."""
        code = None
        while code is None or not AuthCode.is_available(code=code):
            code = get_random_string(
                length=8,
                # all alphanumeric chars except ambiguous ones (0, O, 1, i, l)
                allowed_chars="23456789ABCDEFGHJKMNPQRSTUVWXYZ",
            )

        return AuthCode.objects.create(
            code=code,
            authorised_by=Professor.objects.get(user__username=data["username"]),
            purpose=data["purpose"],
        )


class Submission(models.Model):
    title = models.CharField(max_length=150)
    subject = models.ForeignKey("Subject", on_delete=models.PROTECT)
    professor = models.ForeignKey(
        "Professor", on_delete=models.PROTECT, blank=True, null=True
    )
    author = models.CharField(max_length=50)
    year = models.IntegerField(choices=Year.choices, default=Year.OTHER)
    type = models.IntegerField(choices=Type.choices, default=Type.OTHER)
    tags = models.ManyToManyField("Tag", related_name="files", blank=True)
    uploaded = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    file = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def prof_name(self):
        """Professor's full name."""
        return self.professor.full_name

    @property
    def subject_slug(self):
        """Subject's slug."""
        return self.subject.slug

    @property
    def type_name(self):
        """Self.type, but resolved as a string."""
        return Type(self.type).label

    @property
    def year_name(self):
        """Self.year, but resolved as a string."""
        return Year(self.year).label

    @staticmethod
    def generate_filename(subject_id, old_filename):
        """Generate a new filename to avoid name conflicts."""
        extension = extension = old_filename.split(".")[-1]

        if extension not in Extensions:
            raise ValueError("Invalid filename extension")

        try:
            file_count = Submission.objects.filter(subject__id=subject_id).count()
            subject_slug = Subject.objects.get(pk=subject_id).slug
        except:
            raise ValueError("Subject does not exist")

        return "Zapiski_{subject_slug}_{count}.{extension}".format(
            subject_slug=subject_slug, count=str(file_count + 1), extension=extension
        )

    @staticmethod
    @transaction.atomic
    def from_form_data(data):
        """Create a Submission object from data returned by UploadForm.

        :param data: Validated form data as returned by UploadFileForm
        """

        data["file"].name = Submission.generate_filename(
            data["subject"], data["file"].name
        )

        s = Submission.objects.create(
            title=data["title"],
            subject=Subject.objects.get(pk=data["subject"]),
            professor=Professor.objects.get(pk=data["professor"]),
            author=data["author"],
            year=Year(int(data["year"])),
            type=data["type"],
            file=data["file"],
        )
        # Submission needs to have a value for field "id" before many-to-many relationship can be used
        for t in data["tags"]:
            tag = Tag.objects.get(pk=t)
            s.tags.add(tag)

        return s
