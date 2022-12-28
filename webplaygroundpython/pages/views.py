from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from .models import Page
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from .forms import PageForm

from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required


@method_decorator(staff_member_required)
def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)

class PageListView(ListView):
    model = Page
    paginate_by = 10
    # template_name = "pages/pages.html" no hace falta, detecta que es page_list

class PageDetailView(DetailView):
    model = Page
    # emplate_name = "pages/page.html"  no hace falta, detecta que es page_detail

@method_decorator(staff_member_required, name='dispatch')
class PageCreateView(CreateView):
    model = Page
    form_class = PageForm
    success_url = reverse_lazy('pages:pages')
    
@method_decorator(staff_member_required, name='dispatch')
class PageUpdateView(UpdateView):
    model = Page
    form_class = PageForm
    template_name_suffix = '_update_form'
    def get_success_url(self):
        return reverse_lazy('pages:update', args=[self.object.id]) + '?ok'

@method_decorator(staff_member_required, name='dispatch')
class PageDeleteView(DeleteView):
    model = Page
    success_url = reverse_lazy('pages:pages')
