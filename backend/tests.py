from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Professor, Subject, AuthCode, Submission, Tag
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

# Professor.authenticate (correct, incorrect, invalid prof)
# Submission.from_form_data
# generate_filename (valid and malicious extension)


class ProfessorTestCase(TestCase):
    def setUp(sel):
        sub = Subject(name="Test subject", slug="test")
        sub.save()
        prof = Professor(
            first_name="Mr.",
            last_name="Tester",
            username="mrtester",
            password="********",
        )
        prof.save()
        prof.subjects.add(sub)

    def test_authenticate_correctly(self):
        self.assertTrue(Professor.authenticate("mrtester", "********"))

    def test_incorrect_credentials(self):
        with self.assertRaises(ValueError):
            Professor.authenticate("mrtester", "' or DROP TABLE users; --")

    def test_invalid_username(self):
        with self.assertRaises(ValueError):
            Professor.authenticate("mallory", "my_password")

    def test_no_password(self):
        with self.assertRaises(ValueError):
            Professor.authenticate("mrtester", "")

    def test_full_name(self):
        prof = Professor(
            first_name="Mr.",
            last_name="Tester",
            username="mrtester",
            password="********",
        )
        self.assertEquals(prof.full_name, "Mr. Tester")

    def test_duplicate_username(self):
        prof = Professor(
            first_name="Mr.",
            last_name="Tester",
            username="mrtester",
            password="********",
        )
        with self.assertRaises(IntegrityError):
            prof.save()


class AuthCodeTestCase(TestCase):
    def setUp(self):
        prof = Professor(
            first_name="Mr.",
            last_name="Tester",
            username="mrtester",
            password="********",
        )
        prof.save()
        ac = AuthCode(code="test", authorised_by=prof)
        ac.save()
        subject = Subject(name="Test subject", slug="test")
        subject.save()
        prof.subjects.add(subject)
        prof.save()
        sub = Submission(
            title="Test submission",
            subject=subject,
            professor=prof,
            author="testy",
            year=1,
            type=1,
        )
        sub.save()

    def test_authoriser(self):
        ac = AuthCode.objects.get(code="test")
        self.assertEquals(ac.authoriser, "Mr. Tester")

    def test_unique_code(self):
        prof = Professor.objects.get(username="mrtester")
        with self.assertRaises(IntegrityError):
            ac = AuthCode(code="test", authorised_by=prof)
            ac.save()

    def test_validity_check(self):
        prof = Professor.objects.get(username="mrtester")
        self.assertTrue(AuthCode.is_available("test2"))
        self.assertFalse(AuthCode.is_valid("test2"))
        ac = AuthCode(code="test2", authorised_by=prof)
        ac.save()
        self.assertFalse(AuthCode.is_available("test2"))
        self.assertTrue(AuthCode.is_valid("test2"))

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


class SubmissionTestCase(TestCase):
    def setUp(self):
        subject = Subject(name="Test subject", slug="test")
        subject.save()
        prof = Professor(
            first_name="Mr.",
            last_name="Tester",
            username="mrtester",
            password="********",
        )
        prof.save()

    def test_generate_filename(self):
        sub = Subject.objects.get(slug="test")
        new_filename = Submission.generate_filename(sub.id, "TestFile_102341.docx")
        self.assertEquals(new_filename, "Zapiski_test_1.docx")

    def test_invalid_extension(self):
        sub = Subject.objects.get(slug="test")
        with self.assertRaises(ValueError):
            Submission.generate_filename(sub.id, "trojan.exe")

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
                Tag.name_to_id(name)
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
        self.assertEquals(len(s.tags_arr), len(set(s.tags_arr)))


class TagTestCase(TestCase):
    def setUp(self):
        pass

    def test_name_to_id(self):
        self.assertEquals(Tag.objects.count(), 0)
        for i in range(23):
            id = Tag.name_to_id("tag #" + str(i))
            self.assertEquals(Tag.objects.get(name="tag #" + str(i)).id, id)
        self.assertEquals(Tag.objects.count(), 23)
        for i in range(23):
            id = Tag.name_to_id("tag #" + str(i))
            self.assertEquals(Tag.objects.get(name="tag #" + str(i)).id, id)
        self.assertEquals(Tag.objects.count(), 23)
        self.assertEquals(Tag.objects.get(pk=1).__str__(), "tag #0")
