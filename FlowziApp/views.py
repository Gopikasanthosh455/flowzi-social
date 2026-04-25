from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from FlowziApp.forms import NewPostform
from FlowziApp.models import Likes, Post, Tag
from comment.forms import CommentForm
from comment.models import Comment
from userauths.models import Profile

from django.http import HttpResponseRedirect, JsonResponse



@login_required
def home_page(request):
    post_items = (
        Post.objects.select_related("user", "user__profile")
        .prefetch_related("comment_set", "tags")
        .order_by("-posted", "-id")
    )

    suggested_user_ids = []
    for post in post_items:
        post.latest_comment = post.comment_set.order_by("-date", "-id").first()
        post.is_liked = Likes.objects.filter(user=request.user, post=post).exists()
        if post.user_id != request.user.id and post.user_id not in suggested_user_ids:
            suggested_user_ids.append(post.user_id)

    context = {
        "post_items": post_items,
        "suggested_users": User.objects.filter(id__in=suggested_user_ids[:4]).select_related("profile"),
    }
    return render(request, "home.html", context)


@login_required
def NewPost(request):
    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data["picture"]
            caption = form.cleaned_data["caption"]
            tag_names = [tag.strip() for tag in form.cleaned_data["tags"].split(",") if tag.strip()]

            post = Post.objects.create(picture=picture, caption=caption, user=request.user)
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(title=tag_name)
                post.tags.add(tag)

            return redirect("profile", username=request.user.username)
    else:
        form = NewPostform()

    return render(request, "newpost.html", {"form": form, "page_title": "Create Post"})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == "POST":
        form = NewPostform(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            tag_names = [tag.strip() for tag in request.POST.get("tags", "").split(",") if tag.strip()]
            post.tags.clear()
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(title=tag_name)
                post.tags.add(tag)

            return redirect("post-detail", post.id)
    else:
        form = NewPostform(instance=post, initial={"tags": ", ".join(post.tags.values_list("title", flat=True))})

    return render(request, "newpost.html", {"form": form, "page_title": "Edit Post", "post": post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return redirect("profile", username=request.user.username)


# @login_required
# def like(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     like_relation = Likes.objects.filter(user=request.user, post=post)
#
#     if like_relation.exists():
#         like_relation.delete()
#         post.likes = max(post.likes - 1, 0)
#     else:
#         Likes.objects.create(user=request.user, post=post)
#         post.likes += 1
#
#     post.save()
#     return HttpResponseRedirect(reverse("post-detail", args=[post.id]))
@login_required
def like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_relation = Likes.objects.filter(user=request.user, post=post)

    if like_relation.exists():
        like_relation.delete()
        post.likes = max(post.likes - 1, 0)
        is_liked = False
    else:
        Likes.objects.create(user=request.user, post=post)
        post.likes += 1
        is_liked = True

    post.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "likes": post.likes,
            "is_liked": is_liked,
        })

    return HttpResponseRedirect(reverse("post-detail", args=[post.id]))


@login_required
def PostDetail(request, post_id):
    post = get_object_or_404(Post.objects.select_related("user", "user__profile"), id=post_id)
    comments = Comment.objects.filter(post=post, parent=None).select_related("user", "user__profile").order_by("-date", "-id")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            return HttpResponseRedirect(reverse("post-detail", args=[post.id]))
    else:
        form = CommentForm()

    return render(request, "post-details.html", {"post": post, "comments": comments, "form": form})


@login_required
def favourite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.favourite.filter(id=post_id).exists():
        profile.favourite.remove(post)
    else:
        profile.favourite.add(post)

    return HttpResponseRedirect(reverse("post-detail", args=[post.id]))
