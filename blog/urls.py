from django.urls import path
from blog.views import *
from blog.feeds import LatestEntriesFeed, AtomSiteNewsFeed
from . import views


app_name ='blog'

urlpatterns = [
    
    path('', blog_view, name='index'),
    path('post/<int:pid>/', blog_single, name='single'),  # با post/
    path('<int:pid>/', blog_single, name='single_direct'),  # بدون post/ برای سازگاری
    path('category/<str:cat_name>/', blog_category, name='category'),
    path('tag/<str:tag_name>/', blog_tag, name='tag'),
    path('author/<str:author_username>/', blog_author, name='author'),
    path('search/', blog_search, name='search'),
    path('rss/feed/', LatestEntriesFeed(), name='rss_feed'),
    path('atom/feed/', AtomSiteNewsFeed(), name='atom_feed'),
    # path('post/<int:pid>/', views.post_detail, name='single'),
    ]