from django.contrib import admin
from website.models import Contact,NewsletterSubscriber

# Register your models here.
class ContactAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_date'
    empty_value_display = "-empty-"  
    list_display = ('name','email','created_date')
    list_filter =('email',)         
    search_fields = ['name','message']
    
@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_date', 'status']
    list_filter = ['status', 'created_date']
    search_fields = ['email']
    
admin.site.register(Contact,ContactAdmin)
# admin.site.register(Newsletter)