from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from directMessage.models import Message


def build_inbox_context(user, active_username=None):
    conversations = Message.get_message(user)
    directs = Message.objects.none()
    active_user = None

    if conversations:
        if not active_username:
            active_username = conversations[0]["user"].username

        for conversation in conversations:
            if conversation["user"].username == active_username:
                conversation["unread"] = 0
                active_user = conversation["user"]
                break

    if active_user:
        directs = Message.get_conversation(user, active_user.username)
        directs.filter(is_read=False).update(is_read=True)

    return {
        "conversations": conversations,
        "directs": directs,
        "active_direct": active_username,
        "active_user": active_user,
    }


@login_required
def inbox(request):
    return render(request, "directs/inbox.html", build_inbox_context(request.user))


@login_required
def Directs(request, username):
    return render(request, "directs/inbox.html", build_inbox_context(request.user, username))


@login_required
def SendMessages(request):
    if request.method != "POST":
        return redirect("inbox")

    to_user_username = request.POST.get("to_user")
    body = (request.POST.get("body") or "").strip()

    if not to_user_username or not body:
        return redirect("inbox")

    to_user = get_object_or_404(User, username=to_user_username)
    message = Message.send_message(request.user, to_user, body)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"message": message.serialize()})

    return redirect("directs", username=to_user.username)


@login_required
def UserSearch(request):
    query = request.GET.get("q")
    context = {}

    if query:
        users = User.objects.filter(Q(username__icontains=query)).exclude(id=request.user.id)
        paginator = Paginator(users, 8)
        page_number = request.GET.get("page")
        context = {
            "users": paginator.get_page(page_number),
            "query": query,
        }

    return render(request, "directs/search.html", context)


@login_required
def NewMessage(request, username):
    to_user = get_object_or_404(User, username=username)
    if request.user != to_user and not Message.get_conversation(request.user, to_user.username).exists():
        Message.send_message(request.user, to_user, "Hey! Great to connect on Flowzi.")
    return redirect("directs", username=to_user.username)
