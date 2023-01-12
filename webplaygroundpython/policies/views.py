from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from .models import Policy
from datetime import datetime
from .filters import PolicyFilter
from django_filters.views import FilterView

class PolicyListView(FilterView):
    model = Policy
    template_name = "policies/policies.html"
    paginate_by = 2
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

    # essentially, mirror get behavior exactly on POST
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)