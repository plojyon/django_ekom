from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Professor, Subject, AuthCode, Submission, Tag
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class ProfessorTestCase(TestCase):
    def setUp(sel):
        user = User.objects.create_user(username="mrtester", password="********")
        prof = Professor.objects.create(first_name="Mr.", last_name="Tester", user=user)
        prof.subjects.add(Subject.objects.create(name="Test subject", slug="test"))

    def test_authenticate_correctly(self):
        u = authenticate(username="mrtester", password="********")
        self.assertTrue(u is not None)

    def test_incorrect_password(self):
        u = authenticate(username="mrtester", password="' or DROP TABLE users; --")
        self.assertTrue(u is None)

    def test_invalid_username(self):
        u = authenticate(username="mallory", password="my_password")
        self.assertTrue(u is None)

    def test_full_name(self):
        prof = Professor.objects.get(user__username="mrtester")
        self.assertEquals(prof.full_name, "Mr. Tester")


class AuthCodeTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="mrtester", password="********")
        prof = Professor.objects.create(first_name="Mr.", last_name="Tester", user=user)
        ac = AuthCode.objects.create(code="test", authorised_by=prof)
        subject = Subject.objects.create(name="Test subject", slug="test")
        prof.subjects.add(subject)
        Submission.objects.create(
            title="Test submission",
            subject=subject,
            professor=prof,
            author="testy",
            year=1,
            type=1,
        )

    def test_str(self):
        ac = AuthCode.objects.get(code="test")
        self.assertEquals(ac.__str__(), "test (unused)")
        sub = Submission.objects.get(pk=1)
        AuthCode.use(submission=sub, code=ac.code)
        ac = AuthCode.objects.get(code="test")  # re-fetch the authcode
        self.assertEquals(ac.__str__(), "test (Test submission)")

    def test_authoriser(self):
        ac = AuthCode.objects.get(code="test")
        self.assertEquals(ac.authoriser, "Mr. Tester")

    def test_unique_code(self):
        prof = Professor.objects.get(user__username="mrtester")
        with self.assertRaises(IntegrityError):
            AuthCode.objects.create(code="test", authorised_by=prof)

    def test_validity_check(self):
        prof = Professor.objects.get(user__username="mrtester")
        self.assertTrue(AuthCode.is_available("test2"))
        self.assertFalse(AuthCode.is_valid("test2"))
        ac = AuthCode.objects.create(code="test2", authorised_by=prof)
        self.assertFalse(AuthCode.is_available("test2"))
        self.assertTrue(AuthCode.is_valid("test2"))

    def test_is_valid_nonexistent(self):
        self.assertFalse(AuthCode.is_valid(0))

    def test_is_valid_none(self):
        # this is an important edge case on which some code relies
        self.assertFalse(AuthCode.is_valid(None))

    def test_use(self):
        ac = AuthCode.objects.get(code="test")
        sub = Submission.objects.get(pk=1)
        AuthCode.use(submission=sub, code="test")
        self.assertFalse(AuthCode.is_valid("test"))
        self.assertFalse(AuthCode.is_available("test"))

    def test_use_no_submission(self):
        ac = AuthCode.objects.get(code="test")
        with self.assertRaises(ValueError):
            AuthCode.use(submission=None, code="test")

    def test_from_form_data(self):
        ac = AuthCode.from_form_data(
            {"username": "mrtester", "purpose": "testing purposes"}
        )
        self.assertTrue(ac)


class SubmissionTestCase(TestCase):
    def setUp(self):
        subject = Subject.objects.create(name="Test subject", slug="test")
        user = User.objects.create_user(username="mrtester", password="********")
        prof = Professor.objects.create(first_name="Mr.", last_name="Tester", user=user)
        submission = Submission.objects.create(
            title="title",
            subject=subject,
            professor=prof,
            author="Challe Salle",
            year=3,
            type=4,
        )

    def test_type_name(self):
        subject = Subject.objects.get(slug="test")
        prof = Professor.objects.get(user__username="mrtester")
        submission = Submission.objects.get(pk=1)
        self.assertEquals(submission.type_name, "Laboratorijske vaje")

    def test_year_name(self):
        subject = Subject.objects.get(slug="test")
        prof = Professor.objects.get(user__username="mrtester")
        submission = Submission.objects.get(pk=1)
        self.assertEquals(submission.year_name, "3. letnik")

    def test_generate_filename(self):
        sub = Subject.objects.get(slug="test")
        new_filename = Submission.generate_filename(sub.id, "TestFile_102341.docx")
        self.assertEquals(new_filename, "Zapiski_test_2.docx")

    def test_invalid_extension(self):
        sub = Subject.objects.get(slug="test")
        with self.assertRaises(ValueError):
            Submission.generate_filename(sub.id, "trojan.exe")

    def test_filename_from_nonexistent_subject(self):
        with self.assertRaises(ValueError):
            Submission.generate_filename(83, "how_to_integrate.txt")

    def test_from_form_data(self):
        file = File(open("backend/tests.py", "rb"))
        upload_file = SimpleUploadedFile(
            "data.txt", file.read(), content_type="multipart/form-data"
        )
        form_data = {
            "title": "Test submission",
            "subject": 1,
            "professor": 1,
            "author": "Jakob",
            "year": 3,
            "type": 4,
            "tags": [
                Tag.objects.get_or_create(name=name)[0].id
                for name in ["a", "b", "c", "123", "\\/@@!&#", "+_=``"]
            ],
            "file": upload_file,
        }
        s = Submission.from_form_data(form_data)
        self.assertEquals(s.title, form_data["title"])
        self.assertEquals(s.prof_name, "Mr. Tester")
        self.assertEquals(s.subject_slug, "test")
        self.assertEquals(s.author, "Jakob")
        self.assertEquals(s.year_name, "3. letnik")
        self.assertEquals(s.type_name, "Laboratorijske vaje")
        self.assertEquals(len(s.tags.all()), len(set(s.tags.all())))
