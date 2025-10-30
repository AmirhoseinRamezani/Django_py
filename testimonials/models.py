from django.db import models

class Testimonial(models.Model):
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]
    
    full_name = models.CharField(max_length=100, verbose_name='نام کامل')
    position = models.CharField(max_length=100, blank=True, verbose_name='سمت/شغل')
    company = models.CharField(max_length=100, blank=True, verbose_name='شرکت')
    
    testimonial_text = models.TextField(verbose_name='متن نظر')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, default=5, verbose_name='امتیاز')
    tour = models.ForeignKey('tours.Tour', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تور مربوطه')
    
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True, verbose_name='تصویر')
    video_url = models.URLField(blank=True, verbose_name='لینک ویدیو')
    
    is_approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'نظر مشتری'
        verbose_name_plural = 'نظرات مشتریان'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.full_name} - {self.rating}★"
    
    def get_rating_stars(self):
        return '★' * self.rating
    