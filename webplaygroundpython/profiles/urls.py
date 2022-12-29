from django.urls import path
from .views import ProfileListView, ProfileDetailView

profiles_patterns = (
    [
        path('',ProfileListView.as_view(),name='list'),
        path('detail/<slug:username>',ProfileDetailView.as_view(),name='detail')
    ], 'profiles')