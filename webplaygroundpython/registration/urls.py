from django.urls import path, include
from .views import SignUpCreateView

urlpatterns = [
    path('signup/', SignUpCreateView.as_view(), name='signup')
]