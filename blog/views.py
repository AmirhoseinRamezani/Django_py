from django.shortcuts import render,get_object_or_404
from blog.models import Post
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
# Create your views here.
def blog_view(request, **kwargs):
    posts = Post.objects.filter(status=True)
    
    # مدیریت پارامترهای اختیاری
    # استخراج پارامترها از kwargs
    cat_name = kwargs.get('cat_name')
    author_username = kwargs.get('author_username')
    tag_name = kwargs.get('tag_name')
    
    # فیلتر کردن بر اساس پارامترها
    if cat_name:
        posts = posts.filter(categories__name=cat_name)
    
    if author_username:
        posts = posts.filter(author__username=author_username)
    
    if tag_name:
        posts = posts.filter(tags__name=tag_name)
    
    # صفحه‌بندی
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    
    try:
        posts = paginator.get_page(page_number)
    except PageNotAnInteger:
        posts = paginator.get_page(1)
    except EmptyPage:
        posts = paginator.get_page(paginator.num_pages)
    
    # ایجاد context
    context = {
        'posts': posts,
        'current_cat': cat_name,
        'current_author': author_username,
        'current_tag': tag_name,
    }
    
    return render(request, 'blog/blog-home.html', context)

def blog_single(request,pid):
    post = get_object_or_404(
        Post.objects.select_related('author')
                    .prefetch_related('categories', 'tags')
                    .filter(status=True), 
        pk=pid
    )
    # افزایش تعداد بازدیدها
    post.counted_views += 1
    post.save(update_fields=['counted_views'])    
    
    context = {'post':post}
    return render(request,'blog/blog-single.html',context)


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
    
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page')
    
    try:
        posts = paginator.get_page(page_number)
    except PageNotAnInteger:
        posts = paginator.get_page(1)
    except EmptyPage:
        posts = paginator.get_page(paginator.num_pages)
        
    context = {
            'posts': posts, 
            'query': query,
            # 'results_count': posts.count()  # نمایش تعداد نتایج
            }
    return render(request, 'blog/blog-home.html', context)

def blog_category (request ,cat_name):
    posts = Post.objects.filter(status=1)
    posts = posts.filter(categories__name=cat_name)
    context = {'posts':posts}
    return render(request,'blog/blog-home.html',context)

