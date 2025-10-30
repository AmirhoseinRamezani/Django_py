# testimonials/views.py
from django.shortcuts import render
from django.http import HttpResponse

def testimonial_list(request):
    """لیست نظرات - صفحه موقت"""
    return HttpResponse("""
    <div style='text-align: center; padding: 50px;'>
        <h1>نظرات مشتریان</h1>
        <p>صفحه نظرات به زودی راه‌اندازی می‌شود</p>
        <a href='/'>بازگشت به صفحه اصلی</a>
    </div>
    """)