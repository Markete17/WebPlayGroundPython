from django.urls import path
from . import views
from .views import PolicyListView,PolicyDetailView,PolicyUpdateView,PolicyCreateView,PolicyDeleteView, send_email

policy_patterns = (
    [
    path('', PolicyListView.as_view(), name='policies'),
    path('<int:pk>',PolicyDetailView.as_view(), name='detail'),
    path('update/<int:pk>',PolicyUpdateView.as_view(), name='update'),
    path('create/',PolicyCreateView.as_view(), name='create'),
    path('delete/<int:pk>',PolicyDeleteView.as_view(), name='delete'),
    path('email',send_email, name='email'),
    ], 'policies')