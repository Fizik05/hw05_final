from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        cls.post = Post.objects.create(
            text="ohhhhh, this is test!", author=user
        )

    def test_str(self):
        """Метод __str__ выводит то, что надо."""
        post = str(PostModelTest.post)
        expected_value = "ohhhhh, this is"
        self.assertEqual(
            post, expected_value, "Метод __str__ работает неправильно."
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Test_title",
            slug="group1",
            description="ahahahahhaa, this is test...",
        )

    def test_str(self):
        """Метод __str__ выводит то, что надо."""
        group = str(GroupModelTest.group)
        expected_value = "Test_title"
        self.assertEqual(
            group, expected_value, "Метод __str__ работает неправильно."
        )
