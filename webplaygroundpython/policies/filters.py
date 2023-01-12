import django_filters
from .models import Policy
from django import forms
from .models import PolicyStatus
from django.contrib.auth.models import User

# Django-Filter: https://django-filter.readthedocs.io/en/stable/guide/usage.html#generating-filters-with-meta-fields
class PolicyFilter(django_filters.FilterSet):

    policy_code = django_filters.CharFilter(
        lookup_expr='icontains',
        widget = forms.TextInput(
            attrs={'placeholder':'Número de Póliza', 'class': 'form-control'}
            )
    )

    status = django_filters.ModelChoiceFilter(
        widget=forms.Select(attrs={'class':'form-control'}),
        queryset=PolicyStatus.objects.all(),
        empty_label="Estado Póliza",
    )

    owner = django_filters.ModelChoiceFilter(
        widget=forms.Select(attrs={'class':'form-control'}),
        queryset=User.objects.all(),
        empty_label="Titular",
    )

    created = django_filters.DateFromToRangeFilter(
        lookup_expr='icontains',
        widget=django_filters.widgets.RangeWidget(
            attrs={
                'placeholder': 'DD/MM/YYYY',
                'class':'form-control',
                'type':'date'
            },
        ),
    )

    suspension_date = django_filters.DateFromToRangeFilter(
        lookup_expr='icontains',
        widget=django_filters.widgets.RangeWidget(
            attrs={
                'placeholder': 'DD/MM/YYYY',
                'class':'form-control',
                'type':'date'
            },
        ),
    )
    
    cancellation_date = django_filters.DateFromToRangeFilter(
        lookup_expr='icontains',
        widget=django_filters.widgets.RangeWidget(
            attrs={
                'placeholder': 'DD/MM/YYYY',
                'class':'form-control',
                'type':'date'
            },
        ),
    )



    class Meta:
        model = Policy
        fields = ('policy_code','status','owner','created','suspension_date','cancellation_date')