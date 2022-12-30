from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

def custom_upload_to(instance, filename):
    old_instance = Profile.objects.get(pk=instance.pk)
    old_instance.avatar.delete()
    return 'profiles/'+filename

# Create your models here.
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True, max_length=200)

    class Meta:
        verbose_name = ("Perfil")
        verbose_name_plural = ("Perfiles")
        ordering = ['user__username']

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    ## Comprobar que solo sea de creación y es la primera vez que se guarda esta intancia
    if kwargs.get('created', False):
        Profile.objects.get_or_create(user=instance)

