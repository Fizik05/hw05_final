from http import HTTPStatus

import shutil
import tempfile
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        cls.group = Group.objects.create(
            title="Test_title",
            slug="group1",
            description="ahahahahhaa, this is test...",
        )
        cls.post = Post.objects.create(
            text="Текст", author=cls.user, group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostTemplatesTests.user)

    def test_homepage_template(self):
        """URL-адрес использует соответствующие шаблоны."""
        url_group = reverse(
            "posts:group_posts", kwargs={"slug": PostTemplatesTests.group.slug}
        )
        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": url_group,
            "posts/form.html": reverse("posts:new_post"),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        cls.group = Group.objects.create(
            title="Test_title",
            slug="group1",
            description="ahahahahhaa, this is test...",
        )
        cls.post = Post.objects.create(
            text="Текст",
            author=PostPagesTests.user,
            group=PostPagesTests.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        cache.clear()

    def test_home_page_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        self.assertEqual(first_object.text, PostPagesTests.post.text)
        self.assertEqual(first_object.pub_date, PostPagesTests.post.pub_date)
        self.assertEqual(first_object.author, PostPagesTests.post.author)
        self.assertEqual(first_object.group, PostPagesTests.post.group)
        self.assertEqual(first_object.image, PostPagesTests.post.image)

    def test_group_page_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        url_group = reverse(
            "posts:group_posts", kwargs={"slug": PostPagesTests.group.slug}
        )
        response = self.guest_client.get(url_group)
        first_object = response.context["group"]
        first_object_for_image = response.context["page_obj"][0]
        self.assertEqual(first_object.title, PostPagesTests.group.title)
        self.assertEqual(first_object.slug, PostPagesTests.group.slug)
        self.assertEqual(
            first_object.description, PostPagesTests.group.description
        )
        self.assertEqual(
            first_object_for_image.image,
            PostPagesTests.post.image
        )

    def test_new_post_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        url_post_edit = reverse(
            "posts:post_edit",
            kwargs={"post_id": self.post.id},
        )
        response = self.authorized_client.get(url_post_edit)
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        url_profile = reverse("posts:profile", kwargs={"username": self.user})
        response = self.guest_client.get(url_profile)
        first_object_author = response.context["author"]
        first_object_posts = response.context["page_obj"][0]
        self.assertEqual(first_object_author, PostPagesTests.user)
        self.assertEqual(first_object_posts.image, PostPagesTests.post.image)

    def test_post_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        url_post = reverse(
            "posts:post_detail", kwargs={"post_id": self.post.id}
        )
        response = self.guest_client.get(url_post)
        first_object = response.context["post"]
        self.assertEqual(first_object.text, PostPagesTests.post.text)
        self.assertEqual(first_object.author, PostPagesTests.post.author)
        self.assertEqual(first_object.group, PostPagesTests.post.group)
        self.assertEqual(first_object.image, PostPagesTests.post.image)


class Paginatortests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        Post.objects.bulk_create(
            (Post(text="Текст", author=cls.user) for _ in range(13)),
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Паджинатор на первой странице."""
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        """Паджинатор на второй странице."""
        response = self.guest_client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)


class PostIsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        cls.group = Group.objects.create(
            title="Test_title",
            slug="group1",
            description="ahahahahhaa, this is test...",
        )
        cls.post = Post.objects.create(
            text="Текст", author=cls.user, group=cls.group
        )
        cls.group1 = Group.objects.create(
            title="Test", slug="hoh", description="it is a test"
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostIsTests.user)
        cache.clear()

    def test_post_in_group(self):
        """Проверить пост в группе."""
        response = self.authorized_client.get(
            reverse(
                "posts:group_posts", kwargs={"slug": PostIsTests.group.slug}
            )
        )
        self.assertEqual(
            response.context["group"].title, PostIsTests.group.title
        )
        self.assertEqual(
            response.context["group"].slug, PostIsTests.group.slug
        )
        self.assertEqual(
            response.context["group"].description,
            PostIsTests.group.description,
        )

        first_object = response.context["page_obj"].object_list[0]
        post_text = first_object.text
        post_group = first_object.group

        self.assertEqual(post_text, PostIsTests.post.text)
        self.assertEqual(post_group, PostIsTests.post.group)

        response = self.authorized_client.get(
            reverse(
                "posts:group_posts", kwargs={"slug": PostIsTests.group1.slug}
            )
        )
        assert not response.context["page_obj"].has_next()

    def test_post_in_index(self):
        """Проверить пост на главной странице."""
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"].object_list[0]
        post_text = first_object.text
        self.assertEqual(post_text, PostIsTests.post.text)


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        url = reverse("about:author")
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech(self):
        url = reverse("about:tech")
        response = self.guest_client.get(url)
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


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CacheTests.user)

    def test_cache_post(self):
        post = Post.objects.create(
            text="Пост1;)",
            author=CacheTests.user,
        )
        content_add = self.authorized_client.get(
            reverse("posts:index")).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse("posts:index")
        ).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_delete = self.authorized_client.get(
            reverse(
                "posts:index"
            )
        ).content
        self.assertNotEqual(
            content_add,
            content_delete
        )