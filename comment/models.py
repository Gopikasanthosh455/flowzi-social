from django.db import models
from django.contrib.auth.models import User
from FlowziApp.models import Post

# Create your models here.
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # Related to a post
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Comment author
    body = models.TextField()
    date = models.DateField(auto_now_add=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")

    class Meta:
        ordering = ['-date']