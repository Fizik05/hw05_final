from django.test import Client, TestCase

from ..models import Follow, Group, Post, User


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


class UniqueFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(
            "Pasha", "pasha2009@mail.ru", "123456789"
        )
        cls.second_user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )

    def setUp(self):
        self.following = Follow.objects.get_or_create(
            user=self.first_user,
            author=UniqueFollowTests.second_user
        )
        self.first_authorized_client = Client()
        self.first_authorized_client.force_login(self.first_user)
