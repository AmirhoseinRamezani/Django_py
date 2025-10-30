# destinations/views.py
from django.shortcuts import render
from django.http import HttpResponse

def destination_list(request):
    """لیست مقاصد - صفحه موقت"""
    return HttpResponse("""
    <div style='text-align: center; padding: 50px;'>
        <h1>مقاصد سفر</h1>
        <p>صفحه مقاصد به زودی راه‌اندازی می‌شود</p>
        <a href='/'>بازگشت به صفحه اصلی</a>
    </div>
    """)

def destination_detail(request, pk):
    """جزئیات مقصد - صفحه موقت"""
    return HttpResponse(f"""
    <div style='text-align: center; padding: 50px;'>
        <h1>مقصد شماره {pk}</h1>
        <p>صفحه جزئیات مقصد به زودی راه‌اندازی می‌شود</p>
        <a href='/destinations/'>بازگشت به لیست مقاصد</a>
    </div>
    """)