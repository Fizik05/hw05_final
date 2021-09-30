from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        url_author = reverse("about:author")
        response = self.guest_client.get(url_author)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech(self):
        url_tech = reverse("about:tech")
        response = self.guest_client.get(url_tech)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates(self):
        templates = {
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        for value, expected in templates.items():
            with self.subTest(value=expected):
                response = self.guest_client.get(expected)
                self.assertTemplateUsed(response, value)
