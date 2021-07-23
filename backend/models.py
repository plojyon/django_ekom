from django.db import models
from django.utils.translation import gettext_lazy
from datetime import datetime
import random
from django.conf import settings

class Tag(models.Model):
	name = models.CharField(max_length=50)
	def __str__(self):
		return self.name
	# .files: ManyToManyField(Submission, related_name="tags")

class Professor(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	subjects = models.ManyToManyField('Subject', related_name="professors")
	username = models.CharField(max_length=50)
	password = models.CharField(max_length=50)

	def __str__(self):
		return self.full_name

	@property
	def full_name(self):
		return self.first_name + " " + self.last_name

	@staticmethod
	def authenticate(uname, pw):
		"""Asserts professor uname exists and password matches.
		Returns True or raises Exception."""
		p = Professor.objects.filter(username=uname);
		if p.count() != 1:
			raise ValueError("Professor does not exist")
		p = p[0]
		if p.password != pw:
			raise ValueError("Incorrect password")
		return True;

class Subject(models.Model):
	name = models.CharField(max_length=50)
	slug = models.CharField(max_length=10, unique=True)
	icon = models.CharField(max_length=20, default="fa fa-language")

	def __str__(self):
		return self.name

class AuthCode(models.Model):
	code = models.CharField(max_length=50, unique=True)
	authorised_by = models.ForeignKey('Professor', on_delete=models.PROTECT, related_name='auth_codes')
	authorised_datetime = models.DateTimeField(auto_now_add=True)
	used_datetime = models.DateTimeField(null=True, blank=True)
	used_file = models.OneToOneField('Submission', on_delete=models.SET_NULL, related_name='auth_code', null=True, blank=True)
	purpose = models.CharField(max_length=200)

	def __str__(self):
		return self.code

	@staticmethod
	def is_valid(code):
		"""Checks if the code exists and is unused."""
		ac = AuthCode.objects.filter(code=code)
		if ac.count() != 1: return False
		ac = ac[0]
		return ac.used_datetime is None

	@staticmethod
	def is_available(code):
		"""Checks that a code doesn't yet exist."""
		return AuthCode.objects.filter(code=code).count() == 0

	@staticmethod
	def use(submission, code):
		"""Uses the code on a submission."""
		ac = AuthCode.objects.get(code=code)
		ac.used_datetime = datetime.now()
		ac.used_file = submission

	@staticmethod
	def from_form_data(data):
		"""Create an AuthCode object from data returned by AuthCodeForm."""
		ac = AuthCode()
		# *probably* won't have a conflict ....
		ac.code = str(random.randint(10000000000, 99999999999))
		ac.authorised_by = Professor.objects.get(username=data['username'])
		ac.purpose = data['purpose']
		ac.save()
		return ac.code

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
Extensions = ["pdf", "docx", "txt", "odt", "png", "jpg", "gif", "jpeg", "zip", "7z", "pub"]

class Submission(models.Model):
	title = models.CharField(max_length=150)
	subject = models.ForeignKey('Subject', on_delete=models.PROTECT)
	professor = models.ForeignKey('Professor', on_delete=models.PROTECT)
	author = models.CharField(max_length=50)
	year = models.IntegerField(choices=Year.choices, default=Year.OTHER)
	type = models.IntegerField(choices=Type.choices, default=Type.OTHER)
	tags = models.ManyToManyField('Tag', related_name="files", blank=True)
	uploaded = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	file = models.FileField(blank=True, null=True)

	def __str__(self):
		return self.title

	@property
	def tags_arr(self):
		"""Array of tags on this submission."""
		return [tag.name for tag in self.tags.all()];

	@property
	def prof_name(self):
		"""Professor's full name."""
		return self.professor.full_name

	@property
	def subject_slug(self):
		"""Subject's slug."""
		return self.subject.slug

	@property
	def url(self):
		"""Download link to the resource."""
		return settings.MEDIA_URL + self.file.name

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
		extension = extension = old_filename.split('.')[-1]

		if (extension not in Extensions):
			raise ValueError("Invalid filename extension");

		try:
			file_count = Submission.objects.filter(subject__id=subject_id).count()
			subject_name = Subject.objects.get(pk=subject_id).name
		except:
			raise ValueError("Subject does not exist");

		return "Zapiski_" + subject_name + "_" + str(file_count+1) + "." + extension;

	@staticmethod
	def from_form_data(data):
		"""Create a Submission object from data returned by UploadForm."""
		s = Submission()
		new_filename = Submission.generate_filename(data["subject"], data["file"].name)

		s.title = data["title"]

		try:
			sub = Subject.objects.get(pk=data["subject"])
			s.subject = sub
		except:
			raise ValueError("Subject does not exist.")

		try:
			prof = Professor.objects.get(pk=data["professor"])
			s.professor = prof
		except Exception as e:
			raise ValueError("Professor does not exist: "+str(e))

		s.author = data["author"]
		s.year = Year(int(data["year"]))
		s.type = data["type"]

		s.save() # needs to have a value for field "id" before many-to-many relationship can be used
		for t in data["tags"]:
			tag = Tag.objects.get(pk=t)
			s.tags.add(tag)

		s.file = data["file"]
		s.file.name = new_filename
		s.save()

		return s
