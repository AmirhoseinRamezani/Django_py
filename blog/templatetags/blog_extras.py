# blog/templatetags/blog_extras.py
from django import template

register = template.Library()

@register.filter
def truncate_words_html(value, num_words):
    """کوتاه کردن متن با حفظ تگ‌های HTML"""
    from django.utils.text import Truncator
    return Truncator(value).words(num_words, html=True)