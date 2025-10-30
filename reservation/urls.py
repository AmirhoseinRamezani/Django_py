# reservation/urls.py
from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('', views.reservation_list, name='list'),
    path('create/', views.reservation_create, name='create'),
]
