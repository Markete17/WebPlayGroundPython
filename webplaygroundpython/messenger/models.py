from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed

class Message(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("Mensaje")
        verbose_name_plural = ("Mensajes")

class ThreadManager(models.Manager):
    def find(self, *arguments):

        for i, user in enumerate(arguments):
            if i==0:
                queryset = self.filter(users=user)
            else:
                queryset = queryset.filter(users=user)
        if len(queryset) > 0:
            return queryset[0]
        return None

    def find_or_create(self, *arguments):
        thread = self.find(*arguments)
        if thread is None:
            thread = Thread.objects.create()
            for user in arguments:
                thread.users.add(user)
        return thread

class Thread(models.Model):
    users = models.ManyToManyField(User, related_name="threads")
    messages = models.ManyToManyField(Message)

    # Los campos ManyToMany no afectan al updated, se actualizan con la señal
    updated = models.DateTimeField(auto_now=True)

    objects = ThreadManager()

    class Meta:
        ordering = ['-updated']

# Señal para hacer que un hilo solo pueda recibir mensajes de usuario que sí estén en el hilo
def messages_changed(sender, **kwargs):
    instance = kwargs.pop('instance', None)
    action = kwargs.pop('action', None)
    pk_set = kwargs.pop('pk_set', None)

    false_pk_set = set()
    if action == 'pre_add':
        for msg_pk in pk_set:
            msg = Message.objects.get(pk=msg_pk)
            if msg.user not in instance.users.all():
                false_pk_set.add(msg_pk)
        
    # Borrar los mensajes que no forman parte del hilo
    # Metodo conjuntos A-B
    pk_set.difference_update(false_pk_set)

    # Forzar para actualizar el update
    instance.save()

m2m_changed.connect(messages_changed, sender=Thread.messages.through)