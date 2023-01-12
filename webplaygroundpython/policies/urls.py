from django.urls import path
from . import views
from .views import PolicyListView

policy_patterns = (
    [
    path('', PolicyListView.as_view(), name='policies'),
    ], 'policies')