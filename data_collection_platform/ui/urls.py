# ui/urls.py
from django.urls import path
from .views import index, stats


urlpatterns = [
    path('', index, name='home'),
    path('stats/', stats, name='stats'),
]