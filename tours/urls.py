from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list, name='tour_list'),
    path('category/<slug:category_slug>/', views.tour_list, name='tour_list_by_category'),
    path('<slug:slug>/', views.tour_detail, name='tour_detail'),
    path('<slug:slug>/booking/', views.tour_booking, name='tour_booking'),
    path('<slug:slug>/quick-booking/', views.quick_booking, name='quick_booking'),    
    path('booking/<str:booking_reference>/', views.booking_detail, name='booking_detail'),
    path('api/seats/<int:tour_id>/', views.get_available_seats, name='get_available_seats'),
    path('api/apply-discount/', views.apply_discount, name='apply_discount'),
]