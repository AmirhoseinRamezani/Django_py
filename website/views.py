from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponseRedirect
from website.models import Contact
from website.forms import NameForm,ContactForm,NewsletterForm
from django.contrib import messages
from .models import NewsletterSubscriber
from django.contrib import sitemaps
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from blog.models import Post
from destinations.models import Destination
from tours.models import Tour
from testimonials.models import Testimonial
from services.models import Service


# Create your views here.
# from django.http import HttpResponse,JsonResponse
@never_cache
def index_view(request):
    """صفحه اصلی وبسایت - بهینه‌سازی شده"""
    # واکشی پست‌های ویژه برای نمایش در صفحه اصلی
    try:
        featured_posts = Post.objects.filter(status=True)[:3]
    except:
        featured_posts = []
    
    try:
        popular_destinations = Destination.objects.filter(is_popular=True, is_active=True)[:3]
    except:
        popular_destinations = []
    
    try:
        featured_tours = Tour.objects.filter(is_featured=True, is_active=True)[:6]
    except:
        featured_tours = []
    
    try:
        # استفاده از فیلدهای موجود بدون is_active
        testimonials = Testimonial.objects.filter(is_approved=True, is_featured=True)[:4]
    except:
        try:
            # اگر بازهم خطا داد، فقط از is_approved استفاده کن
            testimonials = Testimonial.objects.filter(is_approved=True)[:4]
        except:
            testimonials = []
    
    try:
        services = Service.objects.all()[:4]
    except:
        services = []
    
    context = {
        'featured_posts': featured_posts,
        'popular_destinations': popular_destinations,
        'featured_tours': featured_tours,
        'testimonials': testimonials,
        'services': services,
    }
    return render(request, 'website/index.html', context)

def about_view(request):
    return render(request, 'website/about.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد! با شما تماس خواهیم گرفت.')
            return redirect('website:contact')
        else:
            messages.error(request, 'لطفاً خطاهای زیر را اصلاح کنید.')
    else:
        form = ContactForm()
    
    return render(request, 'website/contact.html', {'form': form})

def newsletter_view(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'ایمیل شما با موفقیت در خبرنامه ثبت شد!✅')
            except:
                messages.info(request, 'این ایمیل قبلاً در خبرنامه ثبت شده است!')
        else:
            messages.error(request, 'لطفاً یک ایمیل معتبر وارد کنید!')
    
    return redirect('website:index')