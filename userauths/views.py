from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve, reverse

from FlowziApp.models import Follow, Post, Stream
from userauths.forms import EditProfileForm, UserRegisterForm
from userauths.models import Profile


def UserProfile(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    url_name = resolve(request.path).url_name

    posts = Post.objects.filter(user=user).order_by("-posted")
    favourite = profile.favourite.all()
    is_saved_tab = url_name == "favourite"

    follow_status = False
    if request.user.is_authenticated:
        follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    paginator = Paginator(favourite if is_saved_tab else posts, 8)
    page_number = request.GET.get("page")

    context = {
        "profile": profile,
        "posts": posts,
        "favourite": favourite,
        "posts_paginator": paginator.get_page(page_number),
        "is_saved_tab": is_saved_tab,
        "post_count": posts.count(),
        "following_count": Follow.objects.filter(follower=user).count(),
        "followers_count": Follow.objects.filter(following=user).count(),
        "follow_status": follow_status,
    }

    return render(request, "profile.html", context)


@login_required
def follow(request, username, option):
    user = request.user
    following = get_object_or_404(User, username=username)

    if user == following:
        return HttpResponseRedirect(reverse("profile", args=[username]))

    relation, _ = Follow.objects.get_or_create(follower=user, following=following)

    if int(option) == 0:
        relation.delete()
        Stream.objects.filter(following=following, user=user).delete()
    else:
        posts = Post.objects.filter(user=following)[:10]
        with transaction.atomic():
            for post in posts:
                Stream.objects.get_or_create(
                    post=post,
                    user=user,
                    following=following,
                    defaults={"date": post.posted},
                )

    return HttpResponseRedirect(reverse("profile", args=[username]))


@login_required
def editProfile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile", username=profile.user.username)
    else:
        form = EditProfileForm(instance=profile)

    return render(request, "edit_profile.html", {"form": form, "profile": profile})


def register(request):
    if request.user.is_authenticated:
        return redirect("home_page")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, f"Welcome to Flowzi, {new_user.username}.")
            return redirect("home_page")
    else:
        form = UserRegisterForm()

    return render(request, "sign_up.html", {"form": form})
