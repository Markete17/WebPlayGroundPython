from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Page
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

# Create your views here.

class PageListView(ListView):
    model = Page
    paginate_by = 10
    # template_name = "pages/pages.html" no hace falta, detecta que es page_list

class PageDetailView(DetailView):
    model = Page
    # emplate_name = "pages/page.html"  no hace falta, detecta que es page_detail