from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponseRedirect
from website.models import Contact
from website.forms import NameForm,ContactForm,NewsletterForm
from django.contrib import messages
from .models import NewsletterSubscriber
from django.contrib import sitemaps
from django.urls import reverse
from django.views.decorators.cache import never_cache


# Create your views here.
# from django.http import HttpResponse,JsonResponse

@never_cache
def index_view(request):    
    return render(request,'website/index.html')

def about_view(request):
    return render(request,'website/about.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            print(f"New contact message from {contact.name} - {contact.email}")
            # # ارسال ایمیل
            # subject = f"New Contact Message: {contact.subject}"
            # message = f"""
            # Name: {contact.name}
            # Email: {contact.email}
            # Subject: {contact.subject}
            # Message: {contact.message}
            # """
            
            # send_mail(
            #     subject,
            #     message,
            #     settings.DEFAULT_FROM_EMAIL,
            #     ['admin@gmail.com'],  # ایمیل مدیر
            #     fail_silently=False,
            # )
            
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
                # اگر ایمیل تکراری باشد
                messages.info(request, 'این ایمیل قبلاً در خبرنامه ثبت شده است!')
        else:
            messages.error(request, 'لطفاً یک ایمیل معتبر وارد کنید!')
    
    return redirect('website:index')