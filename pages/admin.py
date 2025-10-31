# pages/admin.py
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Page, PageSection, PageLink

class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 1
    fields = ['title', 'content', 'image', 'layout', 'order', 'is_active']

class PageLinkInline(admin.TabularInline):
    model = PageLink
    extra = 1
    fields = ['title', 'url', 'is_external', 'order', 'is_active']

class PageAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'page_type', 'status', 'access_level', 
        'show_in_menu', 'author', 'published_date', 'is_published'
    ]
    list_filter = ['page_type', 'status', 'access_level', 'show_in_menu', 'created_date']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_date', 'updated_date']
    inlines = [PageSectionInline, PageLinkInline]
    
    fieldsets = [
        ('اطلاعات اصلی', {
            'fields': ['title', 'slug', 'content', 'excerpt']
        }),
        ('تصاویر', {
            'fields': ['featured_image', 'thumbnail'],
            'classes': ['collapse']
        }),
        ('تنظیمات', {
            'fields': [
                'page_type', 'status', 'access_level',
                'show_in_menu', 'show_in_footer', 'show_featured', 'menu_order'
            ]
        }),
        ('محتواهای مرتبط', {
            'fields': ['related_tours', 'related_posts'],
            'classes': ['collapse']
        }),
        ('سئو', {
            'fields': ['meta_title', 'meta_description', 'meta_keywords'],
            'classes': ['collapse']
        }),
        ('دسترسی‌ها', {
            'fields': ['author', 'editors'],
            'classes': ['collapse']
        }),
        ('تاریخ‌ها', {
            'fields': ['published_date', 'expiration_date'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # کاربران معمولی فقط صفحات خودشان را می‌بینند
        return qs.filter(author=request.user) | qs.filter(editors=request.user)
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if not request.user.is_superuser:
            readonly_fields.extend(['author', 'access_level'])
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    fieldsets = [
        # فیلدست‌های موجود...
        ('انتشار در بلاگ', {
            'fields': ['publish_to_blog', 'blog_post'],
            'classes': ['collapse'],
        }),
    ]
    
    readonly_fields = ['blog_post']
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and (obj.author == request.user or request.user in obj.editors.all()):
            return True
        return False

admin.site.register(Page, PageAdmin)
admin.site.register(PageSection)
admin.site.register(PageLink)

# ایجاد Group مخصوص مدیران صفحات
try:
    page_managers, created = Group.objects.get_or_create(name='Page Managers')
except:
    pass