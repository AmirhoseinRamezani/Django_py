from django.urls import path
from . import views

app_name ='accounts'
 
urlpatterns =[
    path('login',views.login_view,name='login'),
     #  login
    # path('login',views.login_view,name='login'),
     #  logout  
    path('signup',views.signup_view,name='signup')
     #  registration / signup
 ]