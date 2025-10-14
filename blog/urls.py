from django.urls import path
from blog.views import *

app_name ='blog'

urlpatterns = [
    
    # path ('url addree', 'view' , nam e)
   path('', blog_view, name='index'),
   path('<int:pid>' ,blog_single ,name='single')
    
]