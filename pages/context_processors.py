# pages/context_processors.py
from django.db.models import Q
from .models import Page

def pages_menu(request):
    """دریافت صفحات برای منو - بهینه‌سازی شده"""
    try:
        pages = Page.objects.filter(
            status='published',
            show_in_menu=True
        ).order_by('menu_order', 'title')[:8]
        
        return {'pages_menu': pages}
    except:
        # در صورت خطا، لیست خالی برگردان
        return {'pages_menu': []}