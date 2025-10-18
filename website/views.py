from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponseRedirect
from website.models import Contact
from website.forms import NameForm,ContactForm,NewsletterForm
from django.contrib import messages
from .models import NewsletterSubscriber


# Create your views here.
# from django.http import HttpResponse,JsonResponse


def index_view(request):    
    return render(request,'website/index.html')

def about_view(request):
    return render(request,'website/about.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد! ✅')
            return redirect('website:contact')  
    else:
        form = ContactForm()
    
    return render(request,'website/contact.html', {'form': form})


# def newsletter_view(request):
#     if request.method == 'POST':
#         form = NewsletterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             HttpResponseRedirect('/')
#         else:
#             messages.error(request, 'این ایمیل قبلاً ثبت شده است!')    
    
#     return redirect('/')
def newsletter_view(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'ایمیل شما با موفقیت در خبرنامه ثبت شد! ✅')
            except:
                # اگر ایمیل تکراری باشد
                messages.info(request, 'این ایمیل قبلاً در خبرنامه ثبت شده است!')
        else:
            messages.error(request, 'لطفاً یک ایمیل معتبر وارد کنید!')
    
    return redirect('website:index')