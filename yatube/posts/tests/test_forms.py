import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class NewPostCreateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdan", "bboybaga13@mail.ru", "12345678"
        )
        cls.group = Group.objects.create(
            title="This is test-title.",
            slug="test-slug",
            description="OMG, I don't want write it...",
        )
        cls.post = Post.objects.create(
            text="Текст",
            author=NewPostCreateTests.user,
            group=NewPostCreateTests.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(NewPostCreateTests.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "Test_form",
            "group": NewPostCreateTests.group.id,
            "image": uploaded,
        }

        response = self.authorized_client.post(
            reverse("posts:new_post"), data=form_data, follow=True
        )
        user = NewPostCreateTests.user
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={
                    "username": user,
                },
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=user,
                text=form_data["text"],
                group=form_data["group"],
                image="posts/small.gif",
            ).exists()
        )

    def test_create_post_not_group(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Test's post which hasn't group",
        }
        response = self.authorized_client.post(
            reverse("posts:new_post"), data=form_data, follow=True
        )
        user = NewPostCreateTests.user
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={
                    "username": user,
                },
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=user, text=form_data["text"], group=None
            ).exists()
        )

    def test_edit_post(self):
        form_data = {"text": "Test_form", "group": NewPostCreateTests.group.id}

        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={
                    "post_id": NewPostCreateTests.post.id,
                },
            ),
            data=form_data,
            follow=True,
        )
        NewPostCreateTests.post.refresh_from_db()
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": NewPostCreateTests.post.id},
            ),
        )
        self.assertEqual(NewPostCreateTests.post.group.id, form_data["group"])
        self.assertEqual(NewPostCreateTests.post.text, form_data["text"])


class NewCommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            "Bogdaan", "bboybaga16@mail.ru", "123456789"
        )
        cls.post = Post.objects.create(
            text="Текст",
            author=NewCommentTests.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(NewCommentTests.user)

    def test_make_comment(self):
        count_comments = Comment.objects.count()
        form_data = {
            "text": "Test-comment",
        }
        response = self.authorized_client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": NewCommentTests.post.id},
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), count_comments + 1)
        self.assertTrue(
            Comment.objects.filter(
                author=NewCommentTests.user, text=form_data["text"]
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": NewCommentTests.post.id},
            ),
        )
