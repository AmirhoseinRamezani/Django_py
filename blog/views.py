from django.shortcuts import render,get_object_or_404
from blog.models import Post
# Create your views here.
def blog_view(request):
    # post = get_object_or_404(Post.objects.filter(status=1))
    # context = {'posts':post}
    
    posts = Post.objects.filter(status=1)
    return render(request, 'blog/blog-home.html', {'posts': posts})
    # return render(request,'blog/blog-home.html',context)

def blog_single(request,pid):
    # posts = Post.objects.filter(status=1)
    # post = get_object_or_404(posts,pk=pid)
    # post = get_object_or_404(Post.objects.select_related('category') ,pk=pid ,status=1)
    post = get_object_or_404(Post.objects.prefetch_related('categories'), pk=pid, status=1)
    context = {'post':post}
    return render(request,'blog/blog-single.html',context)
