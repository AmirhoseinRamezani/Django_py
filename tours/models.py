from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse

class TourCategory(models.Model):
    """دسته‌بندی تورها"""
    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(unique=True, verbose_name='اسلاگ')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='تصویر')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')

    class Meta:
        verbose_name = 'دسته‌بندی تور'
        verbose_name_plural = 'دسته‌بندی تورها'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

class Transportation(models.Model):
    TRANSPORT_TYPES = [
        ('bus', 'اتوبوس'),
        ('train', 'قطار'),
        ('airplane', 'هواپیما'),
        ('cruise', 'کشتی'),
        ('minibus', 'مینی بوس'),
        ('car', 'خودرو شخصی'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام وسیله نقلیه')
    transport_type = models.CharField(max_length=20, choices=TRANSPORT_TYPES, verbose_name='نوع وسیله')
    capacity = models.PositiveIntegerField(verbose_name='ظرفیت')
    facilities = models.TextField(blank=True, verbose_name='امکانات')
    image = models.ImageField(upload_to='transportations/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'وسیله نقلیه'
        verbose_name_plural = 'وسایل نقلیه'

    def __str__(self):
        return f"{self.get_transport_type_display()} - {self.name}"

class SeatLayout(models.Model):
    """طرح چیدمان صندلی‌ها برای هر وسیله نقلیه"""
    transportation = models.OneToOneField(Transportation, on_delete=models.CASCADE, related_name='layout')
    rows = models.PositiveIntegerField(verbose_name='تعداد ردیف‌ها')
    columns = models.PositiveIntegerField(verbose_name='تعداد ستون‌ها')
    aisle_after_column = models.PositiveIntegerField(default=0, verbose_name='راهرو پس از ستون')
    
    class Meta:
        verbose_name = 'طرح صندلی'
        verbose_name_plural = 'طرح‌های صندلی'

class Seat(models.Model):
    SEAT_CLASSES = [
        ('economy', 'اکونومی'),
        ('business', 'بیزینس'),
        ('first', 'فرست کلاس'),
        ('premium', 'پریمیوم'),
    ]
    
    SEAT_FEATURES = [
        ('window', 'پنجره'),
        ('aisle', 'راهرو'),
        ('extra_legroom', 'فضای اضافی پا'),
        ('emergency_exit', 'کنار در خروج'),
        ('front', 'جلو'),
        ('back', 'عقب'),
    ]
    
    transportation = models.ForeignKey(Transportation, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10, verbose_name='شماره صندلی')
    seat_class = models.CharField(max_length=20, choices=SEAT_CLASSES, default='economy', verbose_name='کلاس صندلی')
    row = models.PositiveIntegerField(verbose_name='ردیف')
    column = models.CharField(max_length=5, verbose_name='ستون')
    features = models.JSONField(default=list, blank=True, verbose_name='ویژگی‌ها')
    price_modifier = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='تغییرات قیمت')
    is_available = models.BooleanField(default=True, verbose_name='قابل رزرو')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'صندلی'
        verbose_name_plural = 'صندلی‌ها'
        unique_together = ['transportation', 'seat_number']
        ordering = ['row', 'column']

    def __str__(self):
        return f"{self.transportation.name} - {self.seat_number}"

    def get_features_display(self):
        feature_names = {
            'window': 'کنار پنجره',
            'aisle': 'کنار راهرو', 
            'extra_legroom': 'فضای اضافی پا',
            'emergency_exit': 'کنار در خروج',
            'front': 'ردیف جلو',
            'back': 'ردیف عقب'
        }
        return [feature_names.get(feature, feature) for feature in self.features]

# مدل TourImage باید قبل از Tour تعریف شود
class TourImage(models.Model):
    image = models.ImageField(upload_to='tours/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='متن جایگزین')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    
    class Meta:
        verbose_name = 'تصویر تور'
        verbose_name_plural = 'تصاویر تور'
        ordering = ['display_order']

    def __str__(self):
        return self.caption or f"تصویر {self.id}"

class Tour(models.Model):
    TOUR_TYPES = [
        ('one_way', 'تور یکطرفه'),
        ('round_trip', 'تور رفت و برگشت'),
        ('multi_city', 'تور چند شهری'),
        ('package', 'تور پکیج کامل'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان تور')
    slug = models.SlugField(unique=True, verbose_name='اسلاگ')
    description = models.TextField(verbose_name='توضیحات کامل')
    short_description = models.TextField(max_length=300, verbose_name='توضیح کوتاه')
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPES, verbose_name='نوع تور')
    category = models.ForeignKey(
        TourCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='دسته‌بندی'
    )
    
    # اطلاعات اصلی
    origin_city = models.CharField(max_length=100, verbose_name='شهر مبدأ')
    destination_city = models.CharField(max_length=100, verbose_name='شهر مقصد')
    duration_days = models.PositiveIntegerField(verbose_name='تعداد روزها')
    duration_nights = models.PositiveIntegerField(verbose_name='تعداد شب‌ها')
    
    # اطلاعات رفت
    departure_datetime = models.DateTimeField(verbose_name='تاریخ و زمان حرکت')
    departure_transportation = models.ForeignKey(
        Transportation, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='departure_tours',
        verbose_name='وسیله نقلیه رفت'
    )
    
    # اطلاعات برگشت (برای تورهای رفت و برگشت)
    return_datetime = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ و زمان برگشت')
    return_transportation = models.ForeignKey(
        Transportation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='return_tours',
        verbose_name='وسیله نقلیه برگشت'
    )
    
    # قیمت‌گذاری
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قیمت پایه')
    child_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='قیمت کودک')
    infant_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='قیمت نوزاد')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='قیمت با تخفیف')
    
    # ظرفیت و وضعیت
    total_capacity = models.PositiveIntegerField(verbose_name='ظرفیت کل')
    available_capacity = models.PositiveIntegerField(verbose_name='ظرفیت باقیمانده')
    min_travelers = models.PositiveIntegerField(default=1, verbose_name='حداقل مسافر')
    max_travelers = models.PositiveIntegerField(default=50, verbose_name='حداکثر مسافر')
    
    # ویژگی‌ها
    featured_image = models.ImageField(upload_to='tours/', verbose_name='تصویر اصلی')
    
    # ✅ اصلاح شده: اضافه کردن related_name متفاوت
    gallery_images = models.ManyToManyField(
        TourImage, 
        blank=True, 
        verbose_name='گالری تصاویر',
        related_name='tours'  # اضافه کردن related_name
    )
    
    includes = models.TextField(verbose_name='خدمات شامل', help_text='هر خدمت در یک خط')
    excludes = models.TextField(verbose_name='خدمات غیرشامل', help_text='هر مورد در یک خط')
    itinerary = models.TextField(verbose_name='برنامه سفر')
    requirements = models.TextField(blank=True, verbose_name='ملزومات سفر')
    
    # وضعیت
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    is_instant_confirmation = models.BooleanField(default=True, verbose_name='تأیید فوری')
    seat_selection_available = models.BooleanField(default=True, verbose_name='انتخاب صندلی فعال')
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تور'
        verbose_name_plural = 'تورها'
        ordering = ['departure_datetime']
        indexes = [
            models.Index(fields=['departure_datetime', 'is_active']),
            models.Index(fields=['tour_type', 'category']),
        ]

    def __str__(self):
        return f"{self.title} - {self.origin_city} به {self.destination_city}"

    def get_absolute_url(self):
        return reverse('tours:detail', kwargs={'slug': self.slug})

    def is_round_trip(self):
        return self.tour_type == 'round_trip'
    
    def is_one_way(self):
        return self.tour_type == 'one_way'
    
    def is_available(self):
        return self.is_active and self.available_capacity > 0
    
    def get_current_price(self):
        return self.discount_price if self.discount_price else self.base_price
    
    def get_duration_display(self):
        return f"{self.duration_days} روز و {self.duration_nights} شب"
    
    def get_includes_list(self):
        return [item.strip() for item in self.includes.split('\n') if item.strip()]
    
    def get_excludes_list(self):
        return [item.strip() for item in self.excludes.split('\n') if item.strip()]

# حالا فیلد tour را به TourImage اضافه می‌کنیم
TourImage.add_to_class('tour', models.ForeignKey(
    Tour, 
    on_delete=models.CASCADE, 
    related_name='images',
    null=True,
    blank=True
))

# مدل TourBooking باید قبل از Passenger تعریف شود
class TourBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('confirmed', 'تأیید شده'),
        ('cancelled', 'لغو شده'),
        ('completed', 'تکمیل شده'),
        ('refunded', 'عودت داده شده'),
    ]
    
    PAYMENT_METHODS = [
        ('online', 'پرداخت آنلاین'),
        ('bank_transfer', 'کارت به کارت'),
        ('cash', 'نقدی'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name='تور')
    booking_reference = models.CharField(max_length=20, unique=True, verbose_name='کد رزرو')
    
    # اطلاعات مسافرین
    adult_count = models.PositiveIntegerField(default=1, verbose_name='تعداد بزرگسال')
    child_count = models.PositiveIntegerField(default=0, verbose_name='تعداد کودک')
    infant_count = models.PositiveIntegerField(default=0, verbose_name='تعداد نوزاد')
    
    # صندلی‌ها
    departure_seats = models.ManyToManyField(Seat, through='SelectedSeat', related_name='departure_bookings')
    return_seats = models.ManyToManyField(
        Seat, 
        through='SelectedReturnSeat', 
        related_name='return_bookings',
        blank=True
    )
    
    # قیمت‌گذاری
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ پایه')
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='مالیات')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='تخفیف')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ کل')
    
    # وضعیت
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True, verbose_name='روش پرداخت')
    payment_status = models.BooleanField(default=False, verbose_name='وضعیت پرداخت')
    
    # اطلاعات اضافی
    special_requests = models.TextField(blank=True, verbose_name='درخواست‌های ویژه')
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name='تماس اضطراری')
    emergency_phone = models.CharField(max_length=20, blank=True, verbose_name='تلفن اضطراری')
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True )
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='انقضای رزرو')

    class Meta:
        verbose_name = 'رزرو تور'
        verbose_name_plural = 'رزروهای تور'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_reference} - {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            import random
            timestamp = int(timezone.now().timestamp())
            self.booking_reference = f"TR{timestamp}{random.randint(1000, 9999)}"
        
        # محاسبه تاریخ انقضا (24 ساعت بعد)
        if not self.expires_at and self.status == 'pending':
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
            
        super().save(*args, **kwargs)

    def get_total_passengers(self):
        return self.adult_count + self.child_count + self.infant_count

    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

# حالا Passenger می‌تواند به TourBooking ارجاع دهد
class Passenger(models.Model):
    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
    ]
    
    booking = models.ForeignKey(TourBooking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=50, verbose_name='نام')
    last_name = models.CharField(max_length=50, verbose_name='نام خانوادگی')
    national_id = models.CharField(max_length=10, blank=True, verbose_name='کدملی')
    date_of_birth = models.DateField(verbose_name='تاریخ تولد')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='جنسیت')
    passenger_type = models.CharField(max_length=10, choices=[
        ('adult', 'بزرگسال'),
        ('child', 'کودک'), 
        ('infant', 'نوزاد')
    ], default='adult', verbose_name='نوع مسافر')
    
    class Meta:
        verbose_name = 'مسافر'
        verbose_name_plural = 'مسافرین'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class SelectedSeat(models.Model):
    booking = models.ForeignKey(TourBooking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, verbose_name='مسافر')
    is_departure = models.BooleanField(default=True, verbose_name='صندلی رفت')
    
    class Meta:
        verbose_name = 'صندلی انتخاب شده'
        verbose_name_plural = 'صندلی‌های انتخاب شده'
        unique_together = ['seat', 'is_departure']

    def __str__(self):
        return f"{self.passenger} - {self.seat.seat_number}"

class SelectedReturnSeat(models.Model):
    booking = models.ForeignKey(TourBooking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, verbose_name='مسافر')
    
    class Meta:
        verbose_name = 'صندلی برگشت انتخاب شده'
        verbose_name_plural = 'صندلی‌های برگشت انتخاب شده'
        unique_together = ['seat', 'booking']

    def __str__(self):
        return f"{self.passenger} - {self.seat.seat_number} (برگشت)"

class Discount(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
    ]
    
    APPLY_TO = [
        ('all_tours', 'همه تورها'),
        ('specific_tours', 'تورهای خاص'),
        ('tour_categories', 'دسته‌بندی تورها'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام تخفیف')
    code = models.CharField(max_length=20, unique=True, verbose_name='کد تخفیف', help_text='کد قابل استفاده برای مشتریان')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, verbose_name='نوع تخفیف')
    value = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='مقدار تخفیف')
    apply_to = models.CharField(max_length=20, choices=APPLY_TO, default='all_tours', verbose_name='اعمال بر')
    
    # محدودیت‌ها
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='حداکثر تخفیف')
    min_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='حداقل مبلغ سفارش')
    max_uses = models.PositiveIntegerField(default=0, verbose_name='حداکثر استفاده', help_text='0 = نامحدود')
    used_count = models.PositiveIntegerField(default=0, verbose_name='تعداد استفاده شده')
    
    # تاریخ‌ها
    valid_from = models.DateField(verbose_name='اعتبار از')
    valid_to = models.DateField(verbose_name='اعتبار تا')
    
    # شرایط
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_public = models.BooleanField(default=True, verbose_name='نمایش عمومی')
    
    # ارتباطات
    tours = models.ManyToManyField('Tour', blank=True, verbose_name='تورهای مشخص')
    categories = models.ManyToManyField('TourCategory', blank=True, verbose_name='دسته‌بندی‌ها')
    
    class Meta:
        verbose_name = 'تخفیف'
        verbose_name_plural = 'تخفیف‌ها'
        ordering = ['-valid_from']
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['valid_from', 'valid_to']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_valid(self):
        """بررسی اعتبار تخفیف"""
        from django.utils import timezone
        today = timezone.now().date()
        return (self.is_active and 
                self.valid_from <= today <= self.valid_to and
                (self.max_uses == 0 or self.used_count < self.max_uses))

    def calculate_discount_amount(self, booking_amount, tour=None, category=None):
        """محاسبه مبلغ تخفیف"""
        if not self.is_valid:
            return 0
        
        # بررسی شرایط اعمال
        if booking_amount < self.min_booking_value:
            return 0
            
        if self.apply_to == 'specific_tours' and tour and tour not in self.tours.all():
            return 0
            
        if self.apply_to == 'tour_categories' and category and category not in self.categories.all():
            return 0
        
        # محاسبه تخفیف
        if self.discount_type == 'percentage':
            discount = (booking_amount * self.value) / 100
        else:
            discount = self.value
        
        # اعمال سقف تخفیف
        if self.max_discount:
            discount = min(discount, self.max_discount)
        
        return discount

    def can_apply_to_tour(self, tour):
        """بررسی امکان اعمال تخفیف روی تور خاص"""
        if not self.is_valid:
            return False
            
        if self.apply_to == 'all_tours':
            return True
        elif self.apply_to == 'specific_tours':
            return tour in self.tours.all()
        elif self.apply_to == 'tour_categories':
            return tour.category in self.categories.all()
        return False

    def use_discount(self):
        """افزایش شمارنده استفاده"""
        if self.max_uses > 0:
            self.used_count += 1
            self.save()

class TourDiscount(models.Model):
    """تخفیف‌های خاص هر تور"""
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='tour_discounts')  # ✅ تغییر related_name
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField(default=0, verbose_name='اولویت')
    
    class Meta:
        verbose_name = 'تخفیف تور'
        verbose_name_plural = 'تخفیف‌های تور'
        ordering = ['-priority']
        unique_together = ['tour', 'discount']

    def __str__(self):
        return f"{self.tour.title} - {self.discount.name}"

class BookingDiscount(models.Model):
    """تخفیف‌های اعمال شده روی هر رزرو"""
    booking = models.ForeignKey(TourBooking, on_delete=models.CASCADE, related_name='applied_discounts')
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مبلغ تخفیف')
    discount_code = models.CharField(max_length=50, blank=True, verbose_name='کد تخفیف استفاده شده')
    
    class Meta:
        verbose_name = 'تخفیف رزرو'
        verbose_name_plural = 'تخفیف‌های رزرو'

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.discount_amount}"