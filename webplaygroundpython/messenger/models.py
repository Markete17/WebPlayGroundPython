from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Message(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("Mensaje")
        verbose_name_plural = ("Mensajes")

class Thread(models.Model):
    users = models.ManyToManyField(User, related_name="threads")
    messages = models.ManyToManyField(Message)
