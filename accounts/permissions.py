from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class CustomPermissions:
    # دسترسی‌های مخصوص Super Admin
    SUPER_ADMIN_PERMISSIONS = [
        ('can_manage_users', 'می‌تواند کاربران را مدیریت کند'),
        ('can_manage_system', 'می‌تواند سیستم را مدیریت کند'),
        ('can_view_all_data', 'می‌تواند تمام داده‌ها را مشاهده کند'),
        ('can_export_data', 'می‌تواند داده‌ها را export کند'),
    ]
    
    # دسترسی‌های مخصوص Tour Admin
    TOUR_ADMIN_PERMISSIONS = [
        ('can_manage_tours', 'می‌تواند تورها را مدیریت کند'),
        ('can_manage_bookings', 'می‌تواند رزروها را مدیریت کند'),
        ('can_manage_categories', 'می‌تواند دسته‌بندی‌ها را مدیریت کند'),
        ('can_manage_transportation', 'می‌تواند وسایل نقلیه را مدیریت کند'),
        ('can_view_financial_reports', 'می‌تواند گزارشات مالی را مشاهده کند'),
    ]
    
    # دسترسی‌های مخصوص Content Admin
    CONTENT_ADMIN_PERMISSIONS = [
        ('can_manage_blog', 'می‌تواند وبلاگ را مدیریت کند'),
        ('can_manage_destinations', 'می‌تواند مقاصد را مدیریت کند'),
        ('can_manage_testimonials', 'می‌تواند نظرات را مدیریت کند'),
        ('can_manage_pages', 'می‌تواند صفحات را مدیریت کند'),
        ('can_manage_media', 'می‌تواند رسانه‌ها را مدیریت کند'),
    ]

def get_user_permissions(user):
    """بررسی دسترسی کاربر بر اساس user_level"""
    if not hasattr(user, 'profile'):
        return []
    
    user_level = user.profile.user_level
    
    if user_level == 'super_admin':
        return [perm[0] for perm in 
                CustomPermissions.SUPER_ADMIN_PERMISSIONS +
                CustomPermissions.TOUR_ADMIN_PERMISSIONS +
                CustomPermissions.CONTENT_ADMIN_PERMISSIONS]
    
    elif user_level == 'admin':
        return [perm[0] for perm in 
                CustomPermissions.TOUR_ADMIN_PERMISSIONS +
                CustomPermissions.CONTENT_ADMIN_PERMISSIONS]
    
    elif user_level == 'writer':
        return [perm[0] for perm in 
                CustomPermissions.CONTENT_ADMIN_PERMISSIONS]
    
    return []

def user_has_permission(user, permission_codename):
    """بررسی آیا کاربر دسترسی خاصی دارد"""
    user_permissions = get_user_permissions(user)
    return permission_codename in user_permissions