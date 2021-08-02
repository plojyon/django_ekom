from django.test import TestCase
from backend.models import Submission, Professor, Tag, Subject
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.urls import reverse


def create_dummy_submission(
    title="Test submission", subject=1, professor=1, year=2, type=3, tags=[]
):
    return Submission.from_form_data(
        {
            "title": title,
            "subject": subject,
            "professor": professor,
            "author": "Jakob",
            "year": year,
            "type": type,
            "tags": tags,
            "file": SimpleUploadedFile(
                "data.txt",
                File(open("gui/tests.py", "rb")).read(),
                content_type="multipart/form-data",
            ),
        }
    )


def create_filter_string(filters):
    return "?" + "&".join([str(name) + "=" + str(filters[name]) for name in filters])


class FiltersTestCase(TestCase):
    def setUp(self):
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
        create_dummy_submission(title="test-submission-ena", year=1)
        create_dummy_submission(title="test-submission-dva", year=2)

    def test_filter_year(self):
        filterstring = create_filter_string({"year": 1})
        response = self.client.get(reverse("submissions_list") + filterstring)
        resp_text = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)

        self.assertTrue("test-submission-ena" in resp_text)
        self.assertFalse("test-submission-dva" in resp_text)

    def test_no_filters(self):
        filterstring = ""
        response = self.client.get(reverse("submissions_list") + filterstring)
        resp_text = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)

        self.assertTrue("test-submission-ena" in resp_text)
        self.assertTrue("test-submission-dva" in resp_text)

    def test_no_results(self):
        filterstring = create_filter_string({"year": 3})
        response = self.client.get(reverse("submissions_list") + filterstring)
        resp_text = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)

        self.assertTrue("Nobena objava ne ustreza vašemu iskanju." in resp_text)


class SubmissionsViewTestCase(TestCase):
    def setUp(self):
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

    def test_empty_submissions_list(self):
        response = self.client.get(reverse("submissions_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "Nobena objava ne ustreza vašemu iskanju."
            in response.content.decode("utf-8")
        )

    def test_only_display_active_tag_filters(self):
        # unused tags
        for i in range(23):
            Tag.name_to_id("tag #" + str(i))
        # used tags
        tags = [
            Tag.name_to_id(name)
            for name in [
                "tag-aass",
                "tag-bssb",
                "c-tag",
                "1taggy23",
                "+_=``",
            ]
        ]
        create_dummy_submission(tags=tags)
        response = self.client.get(reverse("submissions_list"))
        self.assertEqual(response.status_code, 200)

        for tag in Tag.objects.all():
            is_used = tag.files.count() != 0
            is_in_content = tag.name in response.content.decode("utf-8")
            self.assertEquals(is_in_content, is_used)
