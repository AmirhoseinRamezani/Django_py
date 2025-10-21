from django.db import models

# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    subject = models.CharField(max_length=200 ,verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    updated_date = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    
    class Meta:
        verbose_name = 'تماس'
        verbose_name_plural = 'تماس‌ها'
        ordering = ['-created_date']
        
    # def __str__(self):
    #     return self.name
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
# class Newsletter(models.Model):
#     email = models.EmailField(unique=True)
#     def __str__(self):
#         return self.email
class NewsletterSubscriber(models.Model):  # نام جدید
    email = models.EmailField(unique=True, verbose_name='ایمیل')
    status = models.BooleanField(default=True, verbose_name='فعال')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ اشتراک')
    
    class Meta:
        verbose_name = 'مشترک خبرنامه'
        verbose_name_plural = 'مشترکین خبرنامه'
    
    def __str__(self):
        return self.email
    