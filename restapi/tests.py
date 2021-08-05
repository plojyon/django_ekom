from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from backend.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
import json


class SubmissionTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="mrtester", password="********")
        prof = Professor.objects.create(first_name="Mr.", last_name="Tester", user=user)
        test = Subject.objects.create(name="Test Subject", slug="test")
        prof.subjects.add(test)
        AuthCode.objects.create(
            code="this is a valid authcode",
            authorised_by=prof,
            purpose="testing purposes",
        )

    def test_create_authcode(self):
        client = APIClient()
        data = {
            "authorised_by": "mrtester",
            "password": "********",
            "purpose": "some purpose",
        }
        response = client.post("/api/authcodes/", data, format="json")
        self.assertEqual(response.status_code, 201)

    def test_auth_failure(self):
        client = APIClient()
        data = {
            "authorised_by": "mallory",
            "password": "' or DROP TABLE users;--",
            "purpose": "some purpose",
        }
        response = client.post("/api/authcodes/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_authcode_without_purpose(self):
        client = APIClient()
        data = {
            "authorised_by": "test",
            "password": "********",
            "purpose": "",
        }
        response = client.post("/api/authcodes/", data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_submit_submission(self):
        client = APIClient()
        file = File(open("restapi/tests.py", "rb"))
        upload_file = SimpleUploadedFile(
            "data.txt", file.read(), content_type="multipart/form-data"
        )
        data = {
            "file": upload_file,
            "title": "My title",
            "author": "mr_tester",
            "year": "2",
            "professor": "mrtester",
            "subject": "test",
            "tags": "",
            "type": "1",
            "authcode": "this is a valid authcode",
        }
        response = client.post(
            "/api/submissions/",
            data,
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)

    def test_invalid_extension(self):
        client = APIClient()
        file = File(open("restapi/tests.py", "rb"))
        upload_file = SimpleUploadedFile(
            "trojan.exe", file.read(), content_type="multipart/form-data"
        )
        data = {
            "file": upload_file,
            "title": "My title",
            "author": "mr_tester",
            "year": "2",
            "professor": "mrtester",
            "subject": "test",
            "tags": "",
            "type": "1",
            "authcode": "this is a valid authcode",
        }
        response = client.post(
            "/api/submissions/",
            data,
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_submission(self):
        client = APIClient()
        data = {
            "file": "",
            "title": "My title",
            "author": "mr_tester",
            "year": "2",
            "professor": "mrtester",
            "subject": "test",
            "tags": "",
            "type": "1",
            "authcode": "this is a valid authcode",
        }
        response = client.post("/api/submissions/", data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_used_authcode(self):
        client = APIClient()
        file = SimpleUploadedFile(
            "skripta.pdf",
            File(open("restapi/urls.py", "rb")).read(),
            content_type="multipart/form-data",
        )
        data = {
            "file": file,
            "title": "My title",
            "author": "mr_tester",
            "year": "2",
            "professor": "mrtester",
            "subject": "test",
            "tags": "",
            "type": "1",
            "authcode": "this is a valid authcode",
        }
        response = client.post("/api/submissions/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        data["file"] = SimpleUploadedFile(
            "skripta.pdf",
            File(open("restapi/views.py", "rb")).read(),
            content_type="multipart/form-data",
        )
        response = client.post("/api/submissions/", data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_empty_list_submissions(self):
        client = APIClient()

        response = client.get("/api/submissions/", {}, format="json")
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(content["count"], 0)
        self.assertEqual(content["results"], [])

    def test_submission_list(self):
        client = APIClient()
        file = File(open("restapi/tests.py", "rb"))
        upload_file = SimpleUploadedFile(
            "data.txt", file.read(), content_type="multipart/form-data"
        )
        data = {
            "file": upload_file,
            "title": "My title",
            "author": "mr_tester",
            "year": "2",
            "professor": "mrtester",
            "subject": "test",
            "tags": "",
            "type": "1",
            "authcode": "this is a valid authcode",
        }
        response = client.post(
            "/api/submissions/",
            data,
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)

        # now list submissions and assert it's there
        response = client.get("/api/submissions/", {}, format="json")
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(content["count"], 1)
        self.assertEqual(content["results"][0]["title"], "My title")
