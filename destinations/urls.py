# destinations/urls.py
from django.urls import path
from . import views

app_name = 'destinations'

urlpatterns = [
    path('', views.destination_list, name='list'),
    path('<int:pk>/', views.destination_detail, name='detail'),
]