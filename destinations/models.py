from django.db import models


class Destination(models.Model):
    CONTINENTS = [
        ('asia', 'آسیا'),
        ('europe', 'اروپا'),
        ('africa', 'آفریقا'),
        ('north_america', 'آمریکای شمالی'),
        ('south_america', 'آمریکای جنوبی'),
        ('oceania', 'اقیانوسیه'),
        ('middle_east', 'خاورمیانه'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام مقصد')
    country = models.CharField(max_length=100, verbose_name='کشور')
    continent = models.CharField(max_length=20, choices=CONTINENTS, verbose_name='قاره')
    description = models.TextField(verbose_name='توضیحات')
    best_time_to_visit = models.CharField(max_length=200, verbose_name='بهترین زمان بازدید')
    visa_requirements = models.TextField(blank=True, verbose_name='شرایط ویزا')
    climate = models.TextField(blank=True, verbose_name='آب و هوا')
    culture = models.TextField(blank=True, verbose_name='فرهنگ و آداب و رسوم')
    
    featured_image = models.ImageField(upload_to='destinations/', verbose_name='تصویر شاخص')
    
    # ✅ اصلاح شده: اضافه کردن related_name
    gallery_images = models.ManyToManyField(
        'DestinationImage', 
        blank=True, 
        verbose_name='گالری تصاویر',
        related_name='destination_galleries'  # این خط رو اضافه کن
    )
    
    is_popular = models.BooleanField(default=False, verbose_name='محبوب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='متا عنوان')
    meta_description = models.CharField(max_length=300, blank=True, verbose_name='متا توضیحات')
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مقصد'
        verbose_name_plural = 'مقاصد'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    
    def get_absolute_url(self):
        return reverse('destinations:detail', kwargs={'pk': self.pk})

class DestinationImage(models.Model):
    # این فیلد درست است - related_name='images' دارد
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='destinations/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='متن جایگزین')
    
    class Meta:
        verbose_name = 'تصویر مقصد'
        verbose_name_plural = 'تصاویر مقاصد'
    
    def __str__(self):
        return f"Image for {self.destination.name}"