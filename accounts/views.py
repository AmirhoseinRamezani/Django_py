# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.http import Http404
from django.db.models import Sum
from blog.models import Post

# اضافه کردن import فرم‌ها
try:
    from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, ProfileUpdateForm
except ImportError:
    # اگر فرم‌ها وجود ندارند، از فرم‌های پیش‌فرض استفاده کن
    from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
    CustomUserCreationForm = UserCreationForm
    CustomAuthenticationForm = AuthenticationForm

def login_view(request):
    """ویو برای لاگین کاربر"""
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

def signup_view(request):
    """ویو برای ثبت‌نام کاربر"""
    if request.user.is_authenticated:
        messages.info(request, 'برای ایجاد حساب جدید ابتدا خارج شوید')
        return redirect('/')
    
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

@login_required
def logout_view(request):
    """ویو برای خروج کاربر"""
    username = request.user.username
    logout(request)
    messages.success(request, f'خروج {username} با موفقیت انجام شد')
    return redirect('/')

@login_required
def profile_view(request, username=None):
    """نمایش پروفایل کاربر"""
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user
    
    is_own_profile = request.user == profile_user
    
    # دریافت پست‌های کاربر
    user_posts = Post.objects.filter(author=profile_user, status=1).order_by('-published_date')[:5]
    user_posts_count = Post.objects.filter(author=profile_user, status=1).count()
    
    # محاسبه آمار فقط برای بازدیدها
    stats = Post.objects.filter(author=profile_user, status=1).aggregate(
        total_views=Sum('counted_views')
    )
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_posts': user_posts,
        'user_posts_count': user_posts_count,
        'total_views': stats['total_views'] or 0,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit(request):
    """ویرایش پروفایل کاربر"""
    try:
        from .forms import UserUpdateForm, ProfileUpdateForm
    except ImportError:
        # اگر فرم‌ها import نشدن، پیام خطا نمایش بده
        messages.error(request, 'فرم‌های ویرایش پروفایل در دسترس نیستند.')
        return redirect('accounts:profile_view')
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'پروفایل شما با موفقیت بروزرسانی شد!')
            return redirect('accounts:profile_view')
        else:
            messages.error(request, 'لطفاً خطاهای زیر را اصلاح کنید!')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile_edit.html', context)

def profile_list(request):
    """لیست نویسندگان و ادمین‌ها"""
    try:
        from .models import UserProfile
        profiles = UserProfile.objects.filter(
            user_level__in=['writer', 'admin']
        ).select_related('user')
    except:
        # اگر مدل UserProfile وجود ندارد
        profiles = User.objects.filter(is_staff=True)
    
    context = {
        'profiles': profiles
    }
    return render(request, 'accounts/profile_list.html', context)