from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.PageListView.as_view(), name='page_list'),
    path('<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    path('type/<str:page_type>/', views.page_detail_by_type, name='pages_by_type'),
]