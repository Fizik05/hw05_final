from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        cls.not_author = User.objects.create_user(
            "Test_user", "haha@mail.ru", "123678098"
        )
        cls.post = Post.objects.create(
            text="Это всего лишь тест urls...", author=StaticURLTests.user
        )
        cls.group = Group.objects.create(
            title="Test_title",
            slug="group1",
            description="ahahahahhaa, this is test...",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        self.not_author = Client()
        cache.clear()

    def test_pages(self):
        url_index = reverse("posts:index")
        url_group_posts = reverse(
            "posts:group_posts", kwargs={"slug": StaticURLTests.group.slug}
        )
        url_new_post = reverse("posts:new_post")
        url_profile = reverse(
            "posts:profile", kwargs={"username": StaticURLTests.user}
        )
        url_post = reverse(
            "posts:post_detail",
            kwargs={
                "post_id": StaticURLTests.post.id,
            },
        )
        url_edit_post = reverse(
            "posts:post_edit",
            kwargs={
                "post_id": StaticURLTests.post.id,
            },
        )
        client_pages = {
            url_index: self.guest_client,
            url_group_posts: self.guest_client,
            url_new_post: self.authorized_client,
            url_profile: self.guest_client,
            url_post: self.guest_client,
            url_edit_post: self.authorized_client,
        }
        for url, client in client_pages.items():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_for_guest_client(self):
        url = reverse(
            "posts:post_edit",
            kwargs={
                "post_id": StaticURLTests.post.id,
            },
        )
        response = self.guest_client.get(url)
        self.assertRedirects(
            response, f"{reverse('login')}?next=/posts/1/edit/"
        )

    def test_edit_for_not_author(self):
        url = reverse(
            "posts:post_edit",
            kwargs={
                "post_id": StaticURLTests.post.id,
            },
        )
        response = self.not_author.get(url)
        self.assertRedirects(
            response, f"{reverse('login')}?next=/posts/1/edit/"
        )

    def test_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        url_group = reverse(
            "posts:group_posts", kwargs={"slug": StaticURLTests.group.slug}
        )
        url_post_edit = reverse(
            "posts:post_edit",
            kwargs={"post_id": self.post.id},
        )
        templates_url_names = {
            "posts/index.html": "/",
            "posts/group_list.html": url_group,
            "posts/form.html": reverse("posts:new_post"),
            "posts/edit_post.html": url_post_edit,
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
