from django.contrib import admin
from website.models import Contact,NewsletterSubscriber

# Register your models here.
@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_date', 'status']
    list_filter = ['status', 'created_date']
    search_fields = ['email']
    
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_date', 'is_read']
    list_filter = ['is_read', 'created_date']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_date']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "علامت گذاری به عنوان خوانده شده"
    
    actions = [mark_as_read]
    
# admin.site.register(Newsletter)