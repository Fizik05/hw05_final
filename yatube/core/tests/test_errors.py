from http import HTTPStatus

from django.test import Client, TestCase


class ErrorsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404(self):
        response = self.guest_client.get("/sdfvscs/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
