from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *
from django.contrib.admin import AdminSite

# حذف Group پیش‌فرض از ادمین (اختیاری)
admin.site.unregister(Group)

class TourCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'display_order']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # کاربران معمولی فقط موارد فعال را می‌بینند
        return qs.filter(is_active=True)

class TransportationAdmin(admin.ModelAdmin):
    list_display = ['name', 'transport_type', 'capacity', 'is_active']
    list_filter = ['transport_type', 'is_active']
    search_fields = ['name']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_active=True)

class SeatAdmin(admin.ModelAdmin):
    list_display = ['seat_number', 'transportation', 'seat_class', 'is_available']
    list_filter = ['seat_class', 'is_available', 'transportation']
    search_fields = ['seat_number']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_active=True)

class TourAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'origin_city', 'destination_city', 
        'departure_datetime', 'base_price', 'is_active', 'is_featured'
    ]
    list_filter = ['category', 'tour_type', 'is_active', 'is_featured']
    search_fields = ['title', 'origin_city', 'destination_city']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    # فیلدهای مختلف برای سطوح دسترسی مختلف
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            # سوپر ادمین - تمام فیلدها
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
        else:
            # ادمین معمولی - فیلدهای محدود
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
                ('وضعیت', {
                    'fields': ['is_active', 'is_featured']
                })
            ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # ادمین‌های معمولی فقط تورهای فعال را می‌بینند
        return qs.filter(is_active=True)
    
    def has_delete_permission(self, request, obj=None):
        # فقط سوپر ادمین می‌تواند حذف کند
        return request.user.is_superuser


class CustomAdminSite(AdminSite):
    site_header = 'مدیریت تورها'
    site_title = 'پنل مدیریت تورها'
    
    def has_permission(self, request):
        """
        فقط کاربران لاگین‌شده و staff می‌توانند به ادمین دسترسی داشته باشند
        """
        return request.user.is_active and request.user.is_staff

class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0
    fields = ['first_name', 'last_name', 'national_id', 'date_of_birth', 'gender', 'passenger_type']
    
    def has_change_permission(self, request, obj=None):
        # فقط سوپر ادمین و مدیران تور می‌توانند ویرایش کنند
        return request.user.is_superuser or request.user.groups.filter(name='Tour Managers').exists()

class TourBookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference', 'tour', 'user', 'get_total_passengers', 
        'total_amount', 'status', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['booking_reference', 'user__username', 'user__email']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at', 'expires_at']
    inlines = [PassengerInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # ادمین‌های معمولی فقط رزروهای فعال را می‌بینند
        return qs
    
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            # سوپر ادمین - تمام فیلدها
            return [
                ('اطلاعات رزرو', {
                    'fields': ['booking_reference', 'user', 'tour']
                }),
                ('اطلاعات مسافرین', {
                    'fields': ['adult_count', 'child_count', 'infant_count']
                }),
                ('قیمت‌گذاری', {
                    'fields': ['base_amount', 'tax_amount', 'discount_amount', 'total_amount']
                }),
                ('وضعیت', {
                    'fields': ['status', 'payment_method', 'payment_status']
                }),
                ('اطلاعات اضافی', {
                    'fields': ['special_requests', 'emergency_contact', 'emergency_phone']
                }),
                ('متادیتا', {
                    'fields': ['created_at', 'updated_at', 'expires_at'],
                    'classes': ['collapse']
                })
            ]
        else:
            # ادمین معمولی - فیلدهای محدود
            return [
                ('اطلاعات رزرو', {
                    'fields': ['booking_reference', 'user', 'tour']
                }),
                ('اطلاعات مسافرین', {
                    'fields': ['adult_count', 'child_count', 'infant_count']
                }),
                ('قیمت‌گذاری', {
                    'fields': ['base_amount', 'total_amount']
                }),
                ('وضعیت', {
                    'fields': ['status', 'payment_status']
                }),
                ('اطلاعات اضافی', {
                    'fields': ['special_requests', 'emergency_contact', 'emergency_phone']
                })
            ]
    
    def has_delete_permission(self, request, obj=None):
        # فقط سوپر ادمین می‌تواند رزروها را حذف کند
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
        return request.user.is_superuser

# ثبت مدل‌ها در ادمین
admin.site.register(TourCategory, TourCategoryAdmin)
admin.site.register(Transportation, TransportationAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(TourBooking, TourBookingAdmin)
admin.site.register(Discount, DiscountAdmin)