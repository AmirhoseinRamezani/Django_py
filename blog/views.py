from django.shortcuts import render,get_object_or_404,redirect
from blog.models import Post,Comment,Category
from django.db.models import Q,Count
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from blog.forms import CommentForm
from django.contrib import messages
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Prefetch

def blog_view(request):
    """صفحه اصلی بلاگ - بهینه‌سازی شده"""
    posts_list = Post.objects.filter(status=1)\
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
# Create your views here.


def blog_single(request, pid):
    """صفحه تک پست"""
    try:
        post = get_object_or_404(
            Post.objects.select_related('author')
                        .prefetch_related('categories', 'tags')
                        .filter(status=True), 
            pk=pid
        )
        
        # افزایش تعداد بازدیدها
        post.counted_views += 1
        post.save(update_fields=['counted_views'])
        
        # کامنت‌های تأیید شده - شامل اطلاعات کاربر و پروفایل
        comments = Comment.objects.filter(post=post, approved=True)\
            .select_related('post', 'user', 'user__profile')\
            .order_by('-created_date')
        
        # دیباگ - چک کردن اطلاعات کامنت‌ها
        print(f"=== DEBUG COMMENT INFO ===")
        print(f"تعداد کامنت‌ها: {comments.count()}")
        for i, comment in enumerate(comments):
            print(f"کامنت #{i+1}:")
            print(f"  - نام: {comment.name}")
            print(f"  - کاربر: {comment.user}")
            if comment.user:
                print(f"  - پروفایل کاربر: {hasattr(comment.user, 'profile')}")
                if hasattr(comment.user, 'profile'):
                    print(f"  - تصویر پروفایل: {comment.user.profile.profile_image}")
                    print(f"  - URL تصویر: {comment.user.profile.profile_image.url if comment.user.profile.profile_image else 'None'}")
            print("---")
        print(f"=== END DEBUG ===")
        
        # پست قبلی و بعدی
        previous_post = Post.objects.filter(
            status=True, 
            published_date__lt=post.published_date
        ).order_by('-published_date').first()
        
        next_post = Post.objects.filter(
            status=True, 
            published_date__gt=post.published_date
        ).order_by('published_date').first()
        
        # پست‌های مرتبط
        related_posts = Post.objects.filter(
            status=True,
            categories__in=post.categories.all()
        ).exclude(id=post.id).distinct()[:4]
        
        # مدیریت فرم کامنت
        if request.method == 'POST':
            form = CommentForm(request.POST, user=request.user)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                
                if request.user.is_authenticated:
                    # استفاده از نام کامل از پروفایل اگر موجود باشد
                    full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                    if not full_name and hasattr(request.user, 'profile'):
                        full_name = request.user.profile.display_name
                    
                    comment.name = full_name or request.user.username
                    comment.email = request.user.email
                    comment.user = request.user  # ذخیره کاربر در نظر
                    print(f"✅ کامنت با کاربر ذخیره شد: {request.user.username}")
                else:
                    print(f"ℹ️ کامنت مهمان ذخیره شد: {comment.name}")
                
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
        # لاگ کردن خطا برای دیباگ
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in blog_single view: {str(e)}")
        
        # نمایش صفحه 404 در صورت خطا
        return render(request, '404.html', status=404)
        
        
        # پست قبلی و بعدی
        previous_post = Post.objects.filter(
            status=True, 
            published_date__lt=post.published_date
        ).order_by('-published_date').first()
        
        next_post = Post.objects.filter(
            status=True, 
            published_date__gt=post.published_date
        ).order_by('published_date').first()
        
        # پست‌های مرتبط
        related_posts = Post.objects.filter(
            status=True,
            categories__in=post.categories.all()
        ).exclude(id=post.id).distinct()[:4]
        
        # مدیریت فرم کامنت
        if request.method == 'POST':
            form = CommentForm(request.POST, user=request.user)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                
                if request.user.is_authenticated:
                    # استفاده از نام کامل از پروفایل اگر موجود باشد
                    full_name = f"{request.user.first_name} {request.user.last_name}".strip()
                    if not full_name and hasattr(request.user, 'profile'):
                        full_name = request.user.profile.display_name
                    
                    comment.name = full_name or request.user.username
                    comment.email = request.user.email
                    comment.user = request.user  # ذخیره کاربر در نظر
                
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
        # لاگ کردن خطا برای دیباگ
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in blog_single view: {str(e)}")
        
        # نمایش صفحه 404 در صورت خطا
        return render(request, '404.html', status=404)

def blog_search(request):
    """جستجو در بلاگ"""
    query = request.GET.get('s', '').strip()
    if not query:
        messages.info(request, 'لطفا عبارت جستجو را وارد کنید.')
        return redirect('blog:index')
    
    posts = Post.objects.filter(status=True)\
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
    """پست‌های یک دسته‌بندی"""
    posts = Post.objects.filter(status=True, categories__name=cat_name)\
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
    """پست‌های یک تگ"""
    posts = Post.objects.filter(status=True, tags__name=tag_name)\
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
    """پست‌های یک نویسنده"""
    author = get_object_or_404(User, username=author_username)
    posts = Post.objects.filter(status=True, author=author)\
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