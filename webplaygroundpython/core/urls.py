from django.urls import path
from .views import SampleView, HomePageView
from . import views

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('sample/', SampleView.as_view(), name="sample"),
]