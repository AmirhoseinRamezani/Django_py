from django.urls import path
from blog.views import *
from blog.feeds import LatestEntriesFeed, AtomSiteNewsFeed
from . import views


app_name ='blog'

urlpatterns = [
    
    # path ('url addree', 'view' , name)
    path('', blog_view, name='index'),
    path('<int:pid>' ,blog_single ,name='single'),
    path('category/<str:cat_name>' ,blog_view ,name='category'),
    path('tag/<str:tag_name>' ,blog_view ,name='tag'),
    path('author/<str:author_username>' ,blog_view ,name='author'),
    path('search/',blog_search,name='search'),
    path('rss/feed/', LatestEntriesFeed(), name='rss_feed'),
    path('atom/feed/', AtomSiteNewsFeed(), name='atom_feed'),
    path('post/<int:pid>/', views.post_detail, name='single'),
    ]