from django.db import models

class Service(models.Model):
    SERVICE_TYPES = [
        ('flight', 'پرواز'),
        ('hotel', 'هتل'),
        ('visa', 'ویزا'),
        ('insurance', 'بیمه مسافرتی'),
        ('transfer', 'ترانسفر فرودگاهی'),
        ('tour_guide', 'راهنمای تور'),
        ('car_rental', 'اجاره ماشین'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام خدمت')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, verbose_name='نوع خدمت')
    description = models.TextField(verbose_name='توضیحات')
    features = models.TextField(verbose_name='ویژگی‌ها', help_text='هر ویژگی در یک خط')
    price_range = models.CharField(max_length=100, blank=True, verbose_name=' محدوده قیمت')
    
    icon = models.CharField(max_length=50, blank=True, verbose_name='آیکون')
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name='تصویر')
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'خدمت'
        verbose_name_plural = 'خدمات'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_features_list(self):
        return [feature.strip() for feature in self.features.split('\n') if feature.strip()]