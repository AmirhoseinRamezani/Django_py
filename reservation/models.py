from django.db import models
from django.contrib.auth.models import User
from tours.models import Tour
import random
import string

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),
        ('confirmed', 'تأیید شده'),
        ('paid', 'پرداخت شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تکمیل شده'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('failed', 'پرداخت ناموفق'),
        ('refunded', 'عودت داده شده'),
    ]
    
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name='تور')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='کاربر')
    
    # اطلاعات مسافر اصلی
    main_traveler_name = models.CharField(max_length=100, verbose_name='نام مسافر اصلی')
    main_traveler_email = models.EmailField(verbose_name='ایمیل مسافر اصلی')
    main_traveler_phone = models.CharField(max_length=20, verbose_name='تلفن مسافر اصلی')
    main_traveler_national_id = models.CharField(max_length=20, blank=True, verbose_name='کد ملی')
    
    # اطلاعات رزرو
    adult_count = models.PositiveIntegerField(default=1, verbose_name='تعداد بزرگسال')
    child_count = models.PositiveIntegerField(default=0, verbose_name='تعداد کودک')
    infant_count = models.PositiveIntegerField(default=0, verbose_name='تعداد نوزاد')
    
    departure_date = models.DateField(verbose_name='تاریخ حرکت')
    special_requests = models.TextField(blank=True, verbose_name='درخواست‌های ویژه')
    emergency_contact = models.TextField(blank=True, verbose_name='اطلاعات تماس اضطراری')
    
    # اطلاعات پرداخت
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='مبلغ کل')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='مبلغ پرداخت شده')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name='وضعیت پرداخت')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت رزرو')
    reservation_code = models.CharField(max_length=15, unique=True, verbose_name='کد رزرو')
    
    notes = models.TextField(blank=True, verbose_name='یادداشت‌ها')
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'رزرو'
        verbose_name_plural = 'رزروها'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.reservation_code} - {self.main_traveler_name}"
    
    def save(self, *args, **kwargs):
        if not self.reservation_code:
            self.reservation_code = self.generate_reservation_code()
        
        # محاسبه مبلغ کل
        adult_price = self.tour.get_current_price()
        child_price = self.tour.child_price or adult_price * 0.7  # 30% تخفیف برای کودکان
        
        self.total_amount = (self.adult_count * adult_price) + (self.child_count * child_price)
        
        super().save(*args, **kwargs)
    
    def generate_reservation_code(self):
        return 'TRV' + ''.join(random.choices(string.digits, k=8)) + ''.join(random.choices(string.ascii_uppercase, k=4))
    
    def get_travelers_count(self):
        return self.adult_count + self.child_count + self.infant_count
    
    def get_remaining_amount(self):
        return self.total_amount - self.paid_amount

class Traveler(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='travelers')
    full_name = models.CharField(max_length=100, verbose_name='نام کامل')
    birth_date = models.DateField(verbose_name='تاریخ تولد')
    nationality = models.CharField(max_length=50, verbose_name='ملیت')
    passport_number = models.CharField(max_length=20, blank=True, verbose_name='شماره پاسپورت')
    
    class Meta:
        verbose_name = 'مسافر'
        verbose_name_plural = 'مسافرین'
    
    def __str__(self):
        return self.full_name