from django.contrib import admin
from .models import Post, Category, Comment
from accounts.models import UserLevel
from django_summernote.admin import SummernoteModelAdmin

class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('title', 'author', 'status', 'counted_views', 'published_date', 'created_date')
    list_filter = ('status', 'categories', 'published_date', 'created_date')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_date', 'updated_date', 'counted_views')
    list_editable = ('status',) 
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # نویسندگان فقط پست‌های خودشان را می‌بینند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            return qs.filter(author=request.user)
        return qs
    
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or (hasattr(request.user, 'profile') and 
                                       request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]):
            # سوپر ادمین و ادمین تور - تمام فیلدها
            return [
                ('اطلاعات اصلی', {
                    'fields': ('title', 'author', 'content', 'image')
                }),
                ('تنظیمات', {
                    'fields': ('status', 'categories', 'tags', 'counted_views')
                }),
                ('تاریخ‌ها', {
                    'fields': ('published_date', 'created_date', 'updated_date'),
                    'classes': ('collapse',)
                })
            ]
        else:
            # نویسندگان - فیلدهای محدود
            return [
                ('اطلاعات اصلی', {
                    'fields': ('title', 'content', 'image')
                }),
                ('تنظیمات', {
                    'fields': ('categories', 'tags')
                })
            ]
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # نویسندگان نمی‌توانند author و status را تغییر دهند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            if obj:
                readonly_fields.extend(['author', 'status', 'published_date'])
            else:
                readonly_fields.append('author')
        
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        # برای نویسندگان، author را به صورت خودکار تنظیم کن
         # ✅ منطق ساده‌شده: تنظیم خودکار نویسنده و تاریخ انتشار
        if not obj.author:
            obj.author = request.user
        
        # اگر وضعیت به published تغییر کرد، تاریخ انتشار را تنظیم کن
        if obj.status == 'published' and not obj.published_date:
            from django.utils import timezone
            obj.published_date = timezone.now()
        
        # اگر وضعیت از published تغییر کرد، تاریخ انتشار را پاک کن
        if obj.status != 'published':
            obj.published_date = None
            
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        return True
    
    def has_change_permission(self, request, obj=None):
        if obj and hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            return obj.author == request.user
        return True
    
    def has_add_permission(self, request):
        # همه کاربران با دسترسی محتوا می‌توانند پست اضافه کنند
        return True
    
    def has_change_permission(self, request, obj=None):
        if obj and hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            # نویسندگان فقط می‌توانند پست‌های خودشان را ویرایش کنند
            return obj.author == request.user
        return True
    
    def has_delete_permission(self, request, obj=None):
        if obj and hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            # نویسندگان فقط می‌توانند پست‌های خودشان را حذف کنند
            return obj.author == request.user
        return True

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']
    search_fields = ['name']
    
    def has_module_permission(self, request):
        # همه کاربران با دسترسی محتوا می‌توانند دسته‌بندی‌ها را ببینند
        return True
    
    def post_count(self, obj):
        return obj.posts.count(status='published').count()  
    post_count.short_description = 'تعداد پست‌ها'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'approved', 'created_date')
    list_filter = ('approved', 'post', 'created_date')
    search_fields = ['name', 'email', 'message']
    list_editable = ['approved']
    
    def has_module_permission(self, request):
        # همه کاربران با دسترسی محتوا می‌توانند نظرات را مدیریت کنند
        return True

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)