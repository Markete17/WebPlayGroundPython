from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django_filters.views import FilterView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .models import Policy
from datetime import datetime
from .filters import PolicyFilter
from .forms import PolicyForm


class PolicyListView(FilterView):
    model = Policy
    template_name = "policies/policies.html"
    paginate_by = 5
    filterset_class = PolicyFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get('is_paginated', False):
            return context
        paginator = context.get('paginator')
        num_pages = paginator.num_pages
        current_page = context.get('page_obj')
        page_no = current_page.number

        if num_pages <= 11 or page_no <= 6:  # case 1 and 2
            pages = [x for x in range(1, min(num_pages + 1, 12))]
        elif page_no > num_pages - 6:  # case 4
            pages = [x for x in range(num_pages - 10, num_pages + 1)]
        else:  # case 3
            pages = [x for x in range(page_no - 5, page_no + 6)]

        context.update({'pages': pages})
        return context

class PolicyDetailView(DetailView):
    model = Policy

class PolicyUpdateView(UpdateView):
    model = Policy
    template_name_suffix = '_update_form'
    form_class = PolicyForm

    def get_success_url(self):
        return reverse_lazy('policies:update', args=[self.object.pk]) + '?ok'

class PolicyCreateView(CreateView):
    model = Policy
    template_name_suffix = '_create_form'
    form_class = PolicyForm

    def get_success_url(self):
        return reverse_lazy('policies:detail', args=[self.object.pk])

class PolicyDeleteView(DeleteView):
    model = Policy

    def get_success_url(self):
        return reverse_lazy('policies:policies')
