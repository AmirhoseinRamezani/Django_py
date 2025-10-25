from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post,Comment
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from blog.forms import CommentForm
from django.contrib import messages
from django.http import Http404


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

def blog_single(request, pid):
    post = get_object_or_404(Post.objects.select_related('author')
                    .prefetch_related('categories', 'tags')
                    .filter(status=True), 
        pk=pid
    )
    
    comments = Comment.objects.filter(post=post, approved=True).order_by('-created_date')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # تنظیم خودکار پست برای کامنت
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            
            messages.success(request, 'Your comment was submitted successfully and is awaiting approval.')
            form = CommentForm()  # فرم خالی برای نمایش مجدد
        else:
            messages.error(request, 'There was an error submitting your comment. Please check the form.')
    else:
        form = CommentForm(initial={'post': post.id})
    
    # افزایش تعداد بازدیدها
    post.counted_views += 1
    post.save(update_fields=['counted_views'])
    
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'blog/blog-single.html', context)

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

def post_detail(request, pid):
    """
    نمایش جزئیات پست و مدیریت نظرات
    """
    try:
        # دریافت پست یا نمایش خطای 404 اگر وجود نداشته باشد
        post = get_object_or_404(Post, id=pid, status=True)
        
        if request.method == 'POST':
            # ایجاد فرم با داده‌های ارسالی
            form = CommentForm(request.POST)
            
            if form.is_valid():
                # ذخیره نظر با commit=False برای اضافه کردن اطلاعات اضافی
                comment = form.save(commit=False)
                
                # اگر کاربر لاگین کرده، اطلاعات از پروفایل کاربر گرفته شود
                if request.user.is_authenticated:
                    comment.name = f"{request.user.first_name} {request.user.last_name}"
                    comment.email = request.user.email
                    comment.user = request.user  # اگر فیلد user در مدل Comment وجود دارد
                
                comment.post = post  # ارتباط نظر با پست
                comment.save()
                
                messages.success(request, 'Your comment has been submitted successfully!')
                return redirect('blog:single', pid=post.id)
            else:
                messages.error(request, 'Please correct the errors below.')
        
        else:
            # ایجاد فرم خالی برای GET request
            initial_data = {}
            if request.user.is_authenticated:
                # پر کردن خودکار فیلدها برای کاربران لاگین شده
                initial_data['name'] = f"{request.user.first_name} {request.user.last_name}"
                initial_data['email'] = request.user.email
            
            form = CommentForm(initial=initial_data)
        
        # ارسال پست و فرم به تمپلیت
        context = {
            'post': post,
            'form': form,
        }
        return render(request, 'blog/single.html', context)
    
    except Exception as e:
        # مدیریت خطاهای غیرمنتظره
        raise Http404("Post not found")