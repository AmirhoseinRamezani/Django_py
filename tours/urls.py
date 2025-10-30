# tours/urls.py
from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list, name='list'),
    path('category/<slug:category_slug>/', views.tour_list, name='tour_list_by_category'),
    path('<slug:slug>/', views.tour_detail, name='tour_detail'),
    # path('', views.tour_list, name='list'),
    # path('<int:pk>/', views.tour_detail, name='detail'),
    # path('<int:pk>/booking/', views.tour_booking, name='booking'),
    # path('<int:tour_id>/seats/', views.get_available_seats, name='seats'),
    # path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
]