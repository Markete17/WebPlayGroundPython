from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Thread, Message
from django.http import Http404, JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth.models import User

@method_decorator(login_required, name='dispatch')
# Create your views here.
class ThreadListView(TemplateView):
    template_name = "messenger/thread_list.html"

    """ Filtrar solo los mensajes del usuario conectado
    No hace falta puesto que se puede usar el related para filtrar en la template
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(users=self.request.user)
    """

class ThreadDetailView(DetailView):
    model = Thread

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.users.all():
            raise Http404()
        return obj

def add_message(request, pk):
    json_response = {'created':False}
    if request.user.is_authenticated:
        content = request.GET.get('content',None)
        if content:
            thread = get_object_or_404(Thread, pk=pk)
            message = Message.objects.create(user=request.user, content=content)
            thread.messages.add(message)
            json_response['created'] = True
            if len(thread.messages.all()) == 1:
                json_response['first'] = True
    else:
        raise Http404('User is not authenticated')

    # Convierte Dict a JSON
    return JsonResponse(json_response)

@login_required # Al ser un método no hace falta poner @method_decorator
def start_thread(request, username):
    user = get_object_or_404(User, username=username)
    print(user)
    print(request.user)
    thread = Thread.objects.find_or_create(user, request.user)
    return redirect(reverse_lazy('messenger:detail', args={thread.pk}))