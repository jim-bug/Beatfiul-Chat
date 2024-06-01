import hashlib
from django.db import models
from django.contrib.auth.models import User as DjangoUser

# Create your models here. (DB related)
class Chat(models.Model):
    name = models.CharField(max_length=200)
    chat_id = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    messages = models.JSONField(default=list)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.CharField(max_length=200)

class User(DjangoUser):
    profile_picture_hash = models.CharField(max_length=200, default='')

    def get_profile_picture_url(self):
        return f'/profile_picture/{self.profile_picture_hash}'

