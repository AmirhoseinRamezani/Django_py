from django.contrib import admin
from blog.models import Post, Category
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