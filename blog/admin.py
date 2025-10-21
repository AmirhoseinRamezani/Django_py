from django.contrib import admin
from blog.models import Post, Category,Comment
from django_summernote.admin import SummernoteModelAdmin

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    date_hierarchy = 'created_date'
    empty_value_display = "-empty-"
    list_display = ('title', 'author', 'counted_views', 'status', 
                   'published_date', 'created_date', 'display_tags')
    list_filter = ('status', 'author', 'categories')
    search_fields = ['title', 'content', 'author__username']
    filter_horizontal = ['categories']
    readonly_fields = ['created_date', 'updated_date']


    # فیلدهای نمایش در فرم ویرایش
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'content', 'author', 'image')
        }),
        ('تنظیمات', {
            'fields': ('status', 'categories', 'tags', 'counted_views')
        }),
        ('تاریخ‌ها', {
            'fields': ('published_date', 'created_date', 'updated_date'),
            'classes': ('collapse',)
        })
    )
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = 'تگ‌ها'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.posts.count()  # استفاده از related_name='posts'
    post_count.short_description = 'تعداد پست‌ها'
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    empty_value_display = "-empty-"
    list_display = ('name', 'post', 'email', 'message_summary', 'approved', 'created_date')
    list_filter = ('post', 'approved', 'created_date')
    search_fields = ['name', 'email', 'message', 'subject']
    list_editable = ['approved']
    # readonly_fields = ['created_date', 'updated_date']
    def message_summary(self, obj):
        """نمایش خلاصه‌ای از متن کامنت"""
        if obj.message:
            # نمایش 50 کاراکتر اول و اگر بیشتر بود ...
            return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
        return "-empty-"
    message_summary.short_description = "متن کامنت"
    # اکشن برای تأیید/لغو تأیید کامنت‌ها
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
    approve_comments.short_description = "تأیید کامنت‌های انتخاب شده"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)
    disapprove_comments.short_description = "لغو تأیید کامنت‌های انتخاب شده"
    
    actions = [approve_comments, disapprove_comments]