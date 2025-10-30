# services/views.py
from django.shortcuts import render
from django.http import HttpResponse

def service_list(request):
    """لیست خدمات - صفحه موقت"""
    return HttpResponse("""
    <div style='text-align: center; padding: 50px;'>
        <h1>خدمات ما</h1>
        <p>صفحه خدمات به زودی راه‌اندازی می‌شود</p>
        <a href='/'>بازگشت به صفحه اصلی</a>
    </div>
    """)