# reservation/views.py
from django.shortcuts import render
from django.http import HttpResponse

def reservation_list(request):
    """لیست رزروها - صفحه موقت"""
    return HttpResponse("""
    <div style='text-align: center; padding: 50px;'>
        <h1>رزروهای من</h1>
        <p>صفحه رزروها به زودی راه‌اندازی می‌شود</p>
        <a href='/'>بازگشت به صفحه اصلی</a>
    </div>
    """)

def reservation_create(request):
    """ایجاد رزرو - صفحه موقت"""
    return HttpResponse("""
    <div style='text-align: center; padding: 50px;'>
        <h1>رزرو جدید</h1>
        <p>صفحه رزرو جدید به زودی راه‌اندازی می‌شود</p>
        <a href='/reservation/'>بازگشت به لیست رزروها</a>
    </div>
    """)