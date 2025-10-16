from django.shortcuts import render,get_object_or_404
from blog.models import Post
from django.db.models import Q
# Create your views here.
def blog_view(request,**kwargs):
    # Using kwargs/args for code optimization and readability
    posts = Post.objects.filter(status=1)
    if kwargs.get('cat_name') != None:
        posts=posts.filter(categories__name=kwargs['cat_name'])
    if kwargs.get('author_username') !=None:
        posts=posts.filter(author__username = kwargs['author_username'])
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

def blog_search(request):
    posts = Post.objects.filter(status=1)
    query = request.GET.get('s', '')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()  # برای جلوگیری از تکرار رکوردها
    
    context = {
            'posts': posts, 
            'query': query,
            # 'results_count': posts.count()  # نمایش تعداد نتایج
            }
    print (context)
    return render(request, 'blog/blog-home.html', context)