from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Comment, Category
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.forms import CommentForm
from django.contrib import messages
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Prefetch


def is_post_editor(user):
    """بررسی آیا کاربر ویراستار پست است"""
    return user.is_superuser or user.groups.filter(name__in=['Content Managers', 'Post Editors']).exists()

def is_post_editor(user):
    """بررسی آیا کاربر ویراستار پست است"""
    return user.is_superuser or user.groups.filter(name__in=['Content Managers', 'Post Editors']).exists()

def blog_view(request):
    """صفحه اصلی بلاگ - بهینه‌سازی شده"""
    # ✅ اصلاح شده: استفاده از status='published' به جای status=True
    posts_list = Post.objects.filter(status='published')\
        .select_related('author', 'author__profile')\
        .prefetch_related(
            'categories',
            'tags',
            Prefetch('comments', queryset=Comment.objects.filter(approved=True))
        )\
        .order_by('-published_date')
    
    # تعیین پروفایل برای نمایش
    profile_user = get_default_profile_user(request)
    
    paginator = Paginator(posts_list, 4)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'profile_user': profile_user,
    }
    return render(request, 'blog/blog-home.html', context)

def get_default_profile_user(request):
    """دریافت کاربر پیش‌فرض برای نمایش پروفایل"""
    if request.user.is_authenticated:
        return request.user
    else:
        # واکشی ادمین اصلی سایت
        return User.objects.filter(
            profile__user_level__in=['admin', 'super_admin']
        ).select_related('profile').first()

def blog_single(request, pid):
    """صفحه تک پست - اصلاح شده"""
    try:
        # ✅ اصلاح شده: استفاده از status='published'
        post = get_object_or_404(
            Post.objects.select_related('author')
                        .prefetch_related('categories', 'tags'),
                        
            pk=pid,
            status='published'
        )
        
        # افزایش تعداد بازدیدها
        post.counted_views += 1
        post.save(update_fields=['counted_views'])
        
        # کامنت‌های تأیید شده
        comments = Comment.objects.filter(post=post, approved=True)\
            .select_related('post', 'user', 'user__profile')\
            .order_by('-created_date')
        
        # پست قبلی و بعدی
        previous_post = Post.objects.filter(
            status='published',  # ✅
            published_date__lt=post.published_date
        ).order_by('-published_date').first()
        
        next_post = Post.objects.filter(
            status='published',  # ✅ اصلاح شده
            published_date__gt=post.published_date
        ).order_by('published_date').first()
        
        # پست‌های مرتبط
        related_posts = Post.objects.filter(
            status='published',  # ✅ اصلاح شده
            categories__in=post.categories.all()
        ).exclude(id=post.id).distinct()[:4]
        
        # مدیریت فرم کامنت
        if request.method == 'POST':
            form = CommentForm(request.POST, user=request.user)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                
                if request.user.is_authenticated:
                    full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                    if not full_name and hasattr(request.user, 'profile'):
                        full_name = request.user.profile.display_name
                    
                    comment.name = full_name or request.user.username
                    comment.email = request.user.email
                    comment.user = request.user
                
                comment.save()
                messages.success(request, 'نظر شما با موفقیت ثبت شد و در انتظار تایید است.')
                return redirect('blog:single', pid=pid)
            else:
                messages.error(request, 'خطا در ارسال نظر. لطفا فرم را بررسی کنید.')
        else:
            initial = {}
            if request.user.is_authenticated:
                full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                if not full_name and hasattr(request.user, 'profile'):
                    full_name = request.user.profile.display_name
                
                initial = {
                    'name': full_name or request.user.username,
                    'email': request.user.email
                }
            form = CommentForm(initial=initial, user=request.user)
        
        # پروفایل نویسنده این پست
        profile_user = post.author
        
        context = {
            'post': post,
            'comments': comments,
            'form': form,
            'previous_post': previous_post,
            'next_post': next_post,
            'related_posts': related_posts,
            'profile_user': profile_user,
        }
        return render(request, 'blog/blog-single.html', context)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in blog_single view: {str(e)}")
        return render(request, '404.html', status=404)

def blog_search(request):
    """جستجو در بلاگ - اصلاح شده"""
    query = request.GET.get('s', '').strip()
    if not query:
        messages.info(request, 'لطفا عبارت جستجو را وارد کنید.')
        return redirect('blog:index')
    
    # ✅ اصلاح شده: استفاده از status='published'
    posts = Post.objects.filter(status='published')\
        .select_related('author')\
        .prefetch_related('categories', 'tags')\
        .filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(categories__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # تعیین پروفایل برای نمایش
    if request.user.is_authenticated:
        profile_user = request.user
    else:
        try:
            profile_user = User.objects.filter(profile__user_level='admin').first()
        except:
            profile_user = None
    
    paginator = Paginator(posts, 6)
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
        'results_count': posts.paginator.count,
        'profile_user': profile_user,
    }
    return render(request, 'blog/blog-home.html', context)

def blog_category(request, cat_name):
    """پست‌های یک دسته‌بندی - اصلاح شده"""
    # ✅ اصلاح شده: استفاده از status='published'
    posts = Post.objects.filter(status='published', categories__name=cat_name)\
        .select_related('author')\
        .prefetch_related('categories', 'tags')
    
    # تعیین پروفایل برای نمایش
    if request.user.is_authenticated:
        profile_user = request.user
    else:
        try:
            profile_user = User.objects.filter(profile__user_level='admin').first()
        except:
            profile_user = None
    
    context = {
        'posts': posts,
        'current_cat': cat_name,
        'profile_user': profile_user,
    }
    return render(request, 'blog/blog-home.html', context)

def blog_tag(request, tag_name):
    """پست‌های یک تگ - اصلاح شده"""
    # ✅ اصلاح شده: استفاده از status='published'
    posts = Post.objects.filter(status='published', tags__name=tag_name)\
        .select_related('author')\
        .prefetch_related('categories', 'tags')
    
    # تعیین پروفایل برای نمایش
    if request.user.is_authenticated:
        profile_user = request.user
    else:
        try:
            profile_user = User.objects.filter(profile__user_level='admin').first()
        except:
            profile_user = None
    
    context = {
        'posts': posts,
        'current_tag': tag_name,
        'profile_user': profile_user,
    }
    return render(request, 'blog/blog-home.html', context)

def blog_author(request, author_username):
    """پست‌های یک نویسنده - اصلاح شده"""
    author = get_object_or_404(User, username=author_username)
    # ✅ اصلاح شده: استفاده از status='published'
    posts = Post.objects.filter(status='published', author=author)\
        .select_related('author')\
        .prefetch_related('categories', 'tags')
    
    # پروفایل نویسنده
    profile_user = author
    
    context = {
        'posts': posts,
        'current_author': author,
        'profile_user': profile_user,
    }
    return render(request, 'blog/blog-home.html', context)