from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="from_user")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="to_user")
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("date", "id")

    @staticmethod
    def send_message(from_user, to_user, body):
        sender_message = Message.objects.create(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            body=body,
            is_read=True,
        )
        Message.objects.create(
            user=to_user,
            sender=from_user,
            recipient=from_user,
            body=body,
            is_read=False,
        )
        return sender_message

    @classmethod
    def get_message(cls, user):
        users = []
        messages = cls.objects.filter(user=user).values("recipient").annotate(last=Max("date")).order_by("-last")

        for message in messages:
            users.append(
                {
                    "user": User.objects.get(pk=message["recipient"]),
                    "last": message["last"],
                    "unread": cls.objects.filter(
                        user=user,
                        recipient=message["recipient"],
                        is_read=False,
                    ).count(),
                }
            )

        return users

    @classmethod
    def get_conversation(cls, user, username):
        return cls.objects.filter(user=user, recipient__username=username).select_related(
            "sender",
            "sender__profile",
            "recipient",
            "recipient__profile",
        )

    def serialize(self):
        avatar = ""
        sender_profile = getattr(self.sender, "profile", None)
        if sender_profile and sender_profile.image:
            avatar = sender_profile.image.url

        return {
            "id": self.id,
            "body": self.body,
            "date": self.date.isoformat(),
            "display_date": self.date.strftime("%d %b, %Y %I:%M %p"),
            "sender": self.sender.username,
            "sender_name": self.sender.get_full_name() or self.sender.username,
            "avatar": avatar,
        }
