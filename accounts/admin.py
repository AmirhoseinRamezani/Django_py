from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'پروفایل کاربر'
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('profile_image', 'bio', 'user_level')
        }),
        ('اطلاعات شخصی', {
            'fields': ('birth_date', 'phone_number'),
            'classes': ('collapse',)
        }),
        ('اطلاعات حرفه‌ای', {
            'fields': ('job_title', 'company', 'education_level', 'field_of_study'),
            'classes': ('collapse',)
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('website', 'github', 'linkedin', 'twitter'),
            'classes': ('collapse',)
        }),
    )

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_full_name', 'get_user_level', 'is_staff', 'is_active')
    list_filter = ('profile__user_level', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__bio')
    
    def get_user_level(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_level_display()
        return 'تعریف نشده'
    get_user_level.short_description = 'سطح دسترسی'
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'نام کامل'

# ثبت مجدد UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'user_level', 'job_title', 'created_date')
    list_filter = ('user_level', 'education_level', 'created_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'bio', 'job_title', 'company')
    readonly_fields = ('created_date', 'updated_date')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'user_level')
        }),
        ('اطلاعات پروفایل', {
            'fields': ('profile_image', 'bio')
        }),
        ('اطلاعات شخصی', {
            'fields': ('birth_date', 'phone_number')
        }),
        ('اطلاعات حرفه‌ای', {
            'fields': ('job_title', 'company', 'education_level', 'field_of_study')
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('website', 'github', 'linkedin', 'twitter')
        }),
        ('متادیتا', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'نام کامل'
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'بیوگرافی'
    list_display = ['user', 'bio_preview']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'بیوگرافی'