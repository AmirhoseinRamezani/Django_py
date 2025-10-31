from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from accounts.models import UserLevel
from accounts.permissions import user_has_permission

# حذف Group پیش‌فرض از ادمین (اختیاری)
admin.site.unregister(Group)

class TourCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'display_order', 'tour_count']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # نویسندگان نمی‌توانند دسته‌بندی‌ها را ببینند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            return qs.none()
        return qs
    
    def has_module_permission(self, request):
        # فقط سوپر ادمین و ادمین تور می‌توانند دسته‌بندی‌ها را مدیریت کنند
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]
        return request.user.is_superuser
    
    def tour_count(self, obj):
        return obj.tours.count()
    tour_count.short_description = 'تعداد تورها'

class TransportationAdmin(admin.ModelAdmin):
    list_display = ['name', 'transport_type', 'capacity', 'is_active']
    list_filter = ['transport_type', 'is_active']
    search_fields = ['name']
    
    def has_module_permission(self, request):
        # فقط سوپر ادمین و ادمین تور می‌توانند وسایل نقلیه را مدیریت کنند
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]
        return request.user.is_superuser

class TourAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'origin_city', 'destination_city', 
        'departure_datetime', 'base_price', 'is_active', 'is_featured'
    ]
    list_filter = ['category', 'tour_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['title', 'origin_city', 'destination_city']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # نویسندگان فقط تورهای فعال را می‌بینند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            return qs.filter(is_active=True)
        return qs
    
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or (hasattr(request.user, 'profile') and 
                                       request.user.profile.user_level == UserLevel.SUPER_ADMIN):
            # سوپر ادمین - تمام فیلدها
            return self.get_super_admin_fieldsets()
        elif hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.ADMIN:
            # ادمین تور - فیلدهای کامل مدیریت تور
            return self.get_tour_admin_fieldsets()
        else:
            # نویسندگان - فقط فیلدهای مشاهده‌ای
            return self.get_writer_fieldsets()
    
    def get_super_admin_fieldsets(self):
        return [
            ('اطلاعات اصلی', {
                'fields': ['title', 'slug', 'description', 'short_description', 'category']
            }),
            ('جزئیات سفر', {
                'fields': ['tour_type', 'origin_city', 'destination_city', 'duration_days', 'duration_nights']
            }),
            ('زمان‌بندی', {
                'fields': ['departure_datetime', 'return_datetime']
            }),
            ('وسایل نقلیه', {
                'fields': ['departure_transportation', 'return_transportation']
            }),
            ('قیمت‌گذاری', {
                'fields': ['base_price', 'child_price', 'infant_price', 'discount_price']
            }),
            ('ظرفیت', {
                'fields': ['total_capacity', 'available_capacity', 'min_travelers', 'max_travelers']
            }),
            ('محتوای چندرسانه‌ای', {
                'fields': ['featured_image', 'gallery_images']
            }),
            ('اطلاعات اضافی', {
                'fields': ['includes', 'excludes', 'itinerary', 'requirements']
            }),
            ('وضعیت', {
                'fields': ['is_active', 'is_featured', 'is_instant_confirmation', 'seat_selection_available']
            }),
            ('متادیتا', {
                'fields': ['created_at', 'updated_at'],
                'classes': ['collapse']
            })
        ]
    
    def get_tour_admin_fieldsets(self):
        return [
            ('اطلاعات اصلی', {
                'fields': ['title', 'slug', 'description', 'short_description', 'category']
            }),
            ('جزئیات سفر', {
                'fields': ['tour_type', 'origin_city', 'destination_city', 'duration_days', 'duration_nights']
            }),
            ('زمان‌بندی', {
                'fields': ['departure_datetime', 'return_datetime']
            }),
            ('وسایل نقلیه', {
                'fields': ['departure_transportation', 'return_transportation']
            }),
            ('قیمت‌گذاری', {
                'fields': ['base_price', 'child_price', 'infant_price', 'discount_price']
            }),
            ('ظرفیت', {
                'fields': ['total_capacity', 'available_capacity']
            }),
            ('محتوای چندرسانه‌ای', {
                'fields': ['featured_image', 'gallery_images']
            }),
            ('وضعیت', {
                'fields': ['is_active', 'is_featured']
            })
        ]
    
    def get_writer_fieldsets(self):
        return [
            ('اطلاعات تور', {
                'fields': ['title', 'category', 'tour_type', 'description']
            }),
            ('مشاهده جزئیات', {
                'fields': ['origin_city', 'destination_city', 'duration_days', 'base_price'],
                'classes': ['collapse']
            })
        ]
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        # نویسندگان نمی‌توانند هیچ فیلدی را ویرایش کنند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            readonly_fields.extend([f.name for f in self.model._meta.fields if f.name != 'id'])
        
        return readonly_fields
    
    def has_add_permission(self, request):
        # فقط سوپر ادمین و ادمین تور می‌توانند تور اضافه کنند
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # نویسندگان نمی‌توانند تورها را ویرایش کنند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            return False
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        # فقط سوپر ادمین می‌تواند تورها را حذف کند
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_level == UserLevel.SUPER_ADMIN
        return request.user.is_superuser

class TourBookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference', 'tour', 'user', 'get_total_passengers', 
        'total_amount', 'status', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['booking_reference', 'user__username', 'user__email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at', 'expires_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # نویسندگان نمی‌توانند رزروها را ببینند
        if hasattr(request.user, 'profile') and request.user.profile.user_level == UserLevel.WRITER:
            return qs.none()
        return qs
    
    def has_module_permission(self, request):
        # فقط سوپر ادمین و ادمین تور می‌توانند رزروها را مدیریت کنند
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_level in [UserLevel.SUPER_ADMIN, UserLevel.ADMIN]
        return request.user.is_superuser
    
    def get_total_passengers(self, obj):
        return obj.get_total_passengers()
    get_total_passengers.short_description = 'تعداد مسافرین'

class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'discount_type', 'value', 'is_valid', 'used_count']
    list_filter = ['discount_type', 'is_active', 'apply_to']
    search_fields = ['name', 'code']
    
    def has_module_permission(self, request):
        # فقط سوپر ادمین می‌تواند تخفیف‌ها را مدیریت کند
        if hasattr(request.user, 'profile'):
            return request.user.profile.user_level == UserLevel.SUPER_ADMIN
        return request.user.is_superuser

# ثبت مدل‌ها در ادمین
admin.site.register(TourCategory, TourCategoryAdmin)
admin.site.register(Transportation, TransportationAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TourBooking, TourBookingAdmin)
admin.site.register(Discount, DiscountAdmin)