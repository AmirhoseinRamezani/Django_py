from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    # اگر کاربر از قبل لاگین کرده باشد
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # اعتبارسنجی فیلدهای خالی
        if not username or not password:
            messages.error(request, 'لطفا نام کاربری و رمز عبور را وارد کنید')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'خوش آمدید {user.username}!')
            
            # هدایت به صفحه مورد نظر کاربر یا صفحه پیش‌فرض
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید')
    return redirect('/')

def signup_view(request):
    return render(request, 'accounts/signup.html')