from django import template
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def profile_link(user, current_user, text=None, css_class=""):
    """ایجاد لینک پروفایل - بهینه‌سازی شده"""
    if not user or not isinstance(user, User):
        return text or ""
    
    # واکشی پروفایل کاربر
    if hasattr(user, 'profile'):
        profile = user.profile
        display_text = text or profile.display_name or user.username
    else:
        display_text = text or user.get_full_name() or user.username
    
    # فقط کاربران لاگین شده می‌توانند پروفایل ببینند
    if current_user.is_authenticated:
        url = reverse('accounts:profile_view', kwargs={'username': user.username})
        return format_html(
            '<a href="{}" class="profile-link {}" title="{}">{}</a>',
            url, css_class, f"پروفایل {user.username}", display_text
        )
    else:
        return format_html('<span class="text-muted">{}</span>', display_text)

@register.simple_tag
def profile_image_link(user, current_user, image_url, alt_text, css_class="", size="70px"):
    """
    ایجاد لینک پروفایل برای تصاویر کاربران - نسخه بهینه شده
    """
    if not user or not isinstance(user, User):
        return format_html(
            '<img src="{}" alt="{}" class="{}" style="width: {}; height: {}; object-fit: cover;">',
            image_url, alt_text, css_class, size, size
        )
    
    # فقط اگر کاربر جاری لاگین کرده باشد لینک فعال شود
    if current_user.is_authenticated:
        url = reverse('accounts:profile_view', kwargs={'username': user.username})
        return format_html(
            '<a href="{}" class="profile-image-link" title="مشاهده پروفایل {}">'
            '<img src="{}" alt="{}" class="{}" style="width: {}; height: {}; object-fit: cover;">'
            '</a>',
            url, user.username, image_url, alt_text, css_class, size, size
        )
    else:
        return format_html(
            '<img src="{}" alt="{}" class="{}" style="width: {}; height: {}; object-fit: cover;">',
            image_url, alt_text, css_class, size, size
        )