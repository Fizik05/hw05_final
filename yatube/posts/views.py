from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Comment, Follow, Group, Post, User


@cache_page(20)
@require_http_methods(["GET"])
def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "posts/index.html", {"page_obj": page_obj, "posts": posts}
    )


@require_http_methods(["GET"])
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "posts/group_list.html",
        {"group": group, "posts": posts, "page_obj": page_obj},
    )


@require_http_methods(["GET"])
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    if request.user.is_authenticated:
        authorization = True
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
        else:
            following = False
    else:
        following = False
        authorization = False
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "author": author,
        "page_obj": page,
        "following": following,
        "authorization": authorization
    }
    return render(
        request,
        "posts/profile.html",
        context
    )


@require_http_methods(["GET", "POST"])
def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    user = get_object_or_404(User, username=post.author)
    form = CommentForm(request.POST or None,)
    comments = Comment.objects.filter(post=post)
    return render(
        request,
        "posts/post.html",
        {
            "user": user,
            "post": post,
            "form": form,
            "comments": comments,
        }
    )


@require_http_methods(["POST", "GET"])
@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new = form.save(commit=False)
        new.author = request.user
        new.save()
        return redirect("posts:profile", username=request.user)
    return render(
        request,
        "posts/form.html",
        {
            "form": form,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=request.user)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    if form.is_valid():
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(
        request,
        "posts/edit_post.html",
        {"form": form, "post": post, "is_edit": True}
    )


@require_http_methods(["POST"])
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "posts": posts
    }
    return render(
        request,
        "posts/follow.html",
        context
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:profile", author)


@login_required
def profile_unfollow(request, username):
    follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    follower.delete()
    return redirect("posts:profile", username)
