# pages/templatetags/page_filters.py
from django import template

register = template.Library()

@register.filter
def truncate_smart(value, arg):
    """قطع کردن متن به صورت هوشمند"""
    if len(value) > arg:
        return value[:arg] + '...'
    return value

@register.filter
def get_image_url(obj, default_url='/static/img/default.jpg'):
    """دریافت URL تصویر با مقدار پیش‌فرض"""
    if obj.featured_image:
        return obj.featured_image.url
    return default_url