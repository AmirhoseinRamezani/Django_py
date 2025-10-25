# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.http import Http404
from blog.models import Post, Comment
from blog.forms import CommentForm
def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'شما قبلاً وارد شده‌اید')
        return redirect('/')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'خوش آمدید {user.username}!')
                # هدایت هوشمند
                next_url = request.POST.get('next') or request.GET.get('next') or '/'
                return redirect(next_url)
        else:
            # نمایش خطاهای دقیق
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'next': request.GET.get('next', '')
    }
    return render(request, 'accounts/login.html', context)

@login_required(login_url='/accounts/login/')
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.success(request, f'خروج {username} با موفقیت انجام شد')
    return redirect('/')

def signup_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'برای ایجاد حساب جدید ابتدا خارج شوید')
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # لاگین خودکار بعد از ثبت‌نام
            login(request, user)
            
            messages.success(request, 
                f'حساب کاربری {user.username} با موفقیت ایجاد شد! خوش آمدید'
            )
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'accounts/signup.html', context)

def post_list(request):
    """
    نمایش لیست پست‌ها
    """
    posts = Post.objects.filter(status=True).order_by('-created_date')
    return render(request, 'blog/blog.html', {'posts': posts})

def post_detail(request, pid):
    """
    نمایش جزئیات پست و مدیریت نظرات
    """
    post = get_object_or_404(Post, id=pid, status=True)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            
            if request.user.is_authenticated:
                comment.name = f"{request.user.first_name} {request.user.last_name}"
                comment.email = request.user.email
                comment.user = request.user
            
            comment.post = post
            comment.save()
            
            messages.success(request, 'Your comment has been submitted successfully!')
            return redirect('accounts:single', pid=post.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['name'] = f"{request.user.first_name} {request.user.last_name}"
            initial_data['email'] = request.user.email
        
        form = CommentForm(initial=initial_data)
    
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'blog/single.html', context)