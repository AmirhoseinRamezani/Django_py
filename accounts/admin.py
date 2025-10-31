from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserLevel
from .permissions import user_has_permission, get_user_permissions

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'پروفایل کاربر'
    
    def get_fieldsets(self, request, obj=None):
        # فیلدهای مختلف بر اساس سطح دسترسی کاربر درخواست کننده
        if request.user.is_superuser or (hasattr(request.user, 'profile') and 
                                       request.user.profile.user_level == UserLevel.SUPER_ADMIN):
            # سوپر ادمین - تمام فیلدها
            return (
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
                    'fields': ('website', 'github', 'linkedin', 'twitter', 'instagram'),
                    'classes': ('collapse',)
                }),
            )
        else:
            # سایر کاربران - فیلدهای محدود
            return (
                ('اطلاعات اصلی', {
                    'fields': ('profile_image', 'bio')
                }),
                ('اطلاعات شخصی', {
                    'fields': ('phone_number',),
                    'classes': ('collapse',)
                }),
            )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        # کاربران معمولی نمی‌توانند user_level را تغییر دهند
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN)):
            readonly_fields.append('user_level')
        return readonly_fields

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_full_name', 'get_user_level', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('profile__user_level', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__bio')
    ordering = ('-date_joined',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # اگر کاربر سوپر ادمین نیست، فقط کاربران با سطح پایین‌تر را نشان بده
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN)):
            # ادمین تور می‌تواند نویسندگان و کاربران معمولی را ببیند
            if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.ADMIN:
                return qs.filter(profile__user_level__in=[UserLevel.NORMAL, UserLevel.WRITER])
            # نویسندگان فقط خودشان را می‌بینند
            elif hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
                return qs.filter(id=request.user.id)
        return qs
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        
        # محدود کردن فیلدها برای کاربران غیر سوپر ادمین
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN)):
            # حذف فیلدهای حساس
            if 'Permissions' in [fieldset[0] for fieldset in fieldsets]:
                fieldsets = [fieldset for fieldset in fieldsets if fieldset[0] != 'Permissions']
            if 'Important dates' in [fieldset[0] for fieldset in fieldsets]:
                fieldsets = [fieldset for fieldset in fieldsets if fieldset[0] != 'Important dates']
        
        return fieldsets
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # کاربران غیر سوپر ادمین نمی‌توانند برخی فیلدها را تغییر دهند
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN)):
            readonly_fields.extend(['is_superuser', 'is_staff', 'user_permissions', 'groups', 'last_login', 'date_joined'])
        
        return readonly_fields
    
    def has_add_permission(self, request):
        # فقط سوپر ادمین و ادمین تور می‌توانند کاربر اضافه کنند
        return (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]))
    
    def has_delete_permission(self, request, obj=None):
        # فقط سوپر ادمین می‌تواند کاربر حذف کند
        return (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN))
    
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
    list_display = ('user', 'get_full_name', 'user_level', 'job_title', 'get_profile_completion', 'created_date')
    list_filter = ('user_level', 'education_level', 'created_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'bio', 'job_title', 'company')
    readonly_fields = ('created_date', 'updated_date')
    ordering = ('-created_date',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # فیلتر کردن بر اساس سطح دسترسی کاربر درخواست کننده
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN)):
            if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.ADMIN:
                # ادمین تور می‌تواند نویسندگان و کاربران معمولی را ببیند
                return qs.filter(user_level__in=[UserLevel.NORMAL, UserLevel.WRITER])
            elif hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
                # نویسندگان فقط پروفایل خودشان را می‌بینند
                return qs.filter(user=request.user)
        return qs
    
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or (hasattr(request.user, 'profile') and 
                                       request.user.profile.user_level == UserLevel.SUPER_ADMIN):
            # سوپر ادمین - تمام فیلدها
            return (
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
                    'fields': ('website', 'github', 'linkedin', 'twitter', 'instagram')
                }),
                ('متادیتا', {
                    'fields': ('created_date', 'updated_date'),
                    'classes': ('collapse',)
                }),
            )
        elif hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.ADMIN:
            # ادمین تور - فیلدهای محدود
            return (
                ('اطلاعات کاربر', {
                    'fields': ('user', 'user_level')
                }),
                ('اطلاعات پروفایل', {
                    'fields': ('profile_image', 'bio')
                }),
                ('اطلاعات شخصی', {
                    'fields': ('phone_number',)
                }),
                ('اطلاعات حرفه‌ای', {
                    'fields': ('job_title', 'company')
                }),
            )
        else:
            # نویسندگان - کمترین دسترسی
            return (
                ('اطلاعات پروفایل', {
                    'fields': ('profile_image', 'bio')
                }),
                ('اطلاعات شخصی', {
                    'fields': ('phone_number',)
                }),
            )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        if not (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN)):
            if obj and obj.user_level == UserLevel.SUPER_ADMIN:
                readonly_fields.append('user_level')
            if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
                readonly_fields.extend(['user', 'user_level', 'job_title', 'company', 'education_level', 
                                      'field_of_study', 'website', 'github', 'linkedin', 'twitter', 'instagram'])
        
        return readonly_fields
    
    def has_add_permission(self, request):
        # فقط سوپر ادمین و ادمین تور می‌توانند پروفایل اضافه کنند
        return (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]))
    
    def has_delete_permission(self, request, obj=None):
        # فقط سوپر ادمین می‌تواند پروفایل حذف کند
        return (request.user.is_superuser or 
                (hasattr(request.user, 'profile') and 
                 request.user.profile.user_level == UserLevel.SUPER_ADMIN))
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'نام کامل'
    
    def get_profile_completion(self, obj):
        return f'{obj.get_profile_completion_percentage()}%'
    get_profile_completion.short_description = 'تکمیل پروفایل'
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if obj.bio and len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'بیوگرافی'