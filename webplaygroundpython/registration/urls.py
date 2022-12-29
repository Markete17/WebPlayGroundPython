from django.urls import path, include
from .views import SignUpCreateView, ProfileUpdateView, EmailUpdateView

urlpatterns = [
    path('signup/', SignUpCreateView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('profile/email/', EmailUpdateView.as_view(), name='profile_email')
]