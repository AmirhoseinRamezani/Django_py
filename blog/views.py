from django.shortcuts import render,get_object_or_404
from blog.models import Post
# Create your views here.
def blog_view(request,cat_name=None ,author_username=None):
    posts = Post.objects.filter(status=1)
    if cat_name:
        posts=posts.filter(categories__name=cat_name)
    if author_username:
        posts=posts.filter(author__username = author_username)
    context = {'posts':posts}
    return render(request, 'blog/blog-home.html' ,context)

def blog_single(request,pid):
    post = get_object_or_404(Post.objects.prefetch_related('categories'), pk=pid, status=1)
    context = {'post':post}
    return render(request,'blog/blog-single.html',context)


def blog_category (request ,cat_name):
    posts = Post.objects.filter(status=1)
    posts = posts.filter(categories__name=cat_name)
    context = {'posts':posts}
    return render(request,'blog/blog-home.html',context)