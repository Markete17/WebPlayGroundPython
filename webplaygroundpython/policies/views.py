from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from django_filters.views import FilterView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.http import Http404, JsonResponse

from .models import Policy
from datetime import datetime
from .filters import PolicyFilter
from .forms import PolicyForm

import io
import csv
from django.core.mail import EmailMessage
from django.conf import settings

import datetime

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

def send_email(request):
    json_response = {'created':False}
    # Convierte Dict a JSON
    policy_code = request.GET.get('policy_code')
    id_status = request.GET.get('status')
    id_owner = request.GET.get('owner')

    queryset = Policy.objects.all()
    if(policy_code):
        queryset = queryset.filter(policy_code=policy_code)
    if(id_status):
        queryset = queryset.filter(status__id=id_status)
    if(id_owner):
        queryset = queryset.filter(owner__id=id_owner)
    
    csvfile = io.StringIO()
    csvwriter = csv.writer(csvfile,delimiter=';')
    csvwriter.writerow([
        "Numero Poliza", 
        "Estado Poliza",
        "Titular",
        "Fecha Alta",
        "Fecha Anulacion",
        "Fecha Suspension",
    ])
    for policy in queryset:
        if(policy.created):
            created_format = datetime.date.strftime(policy.created, '%m/%d/%Y')
        else:
            created_format = ''
        if(policy.cancellation_date):
            cancellation_date_format = datetime.date.strftime(policy.cancellation_date, '%m/%d/%Y')
        else:
            cancellation_date_format = ''
        if(policy.suspension_date):
            suspension_date_format = datetime.date.strftime(policy.suspension_date, '%m/%d/%Y')
        else:
            suspension_date_format = ''

        csvwriter.writerow([
            policy.policy_code, 
            policy.status.name,
            policy.owner.username,
            created_format,
            cancellation_date_format,
            suspension_date_format
        ])
    email = EmailMessage(
        subject = 'Polizas',
        body = 'Aquí le enviamos en un documento adjunto su registro de pólizas seleccionadas.',
        from_email = settings.EMAIL_HOST_USER,
        to = ['jiwosip245@v3dev.com'],
        reply_to = ['jiwosip245@v3dev.com'],
    )

    email.attach('policies.csv', csvfile.getvalue(), 'text/csv')

    try:
        email.send()
        json_response['created'] = True
        return JsonResponse(json_response)
    except:
        return JsonResponse(json_response)
    
    