from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.utils import timezone
import os

class Category(models.Model):
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'cat_name': self.name})

class TaggedPost(TaggedItemBase):
    content_object = models.ForeignKey('Post', on_delete=models.CASCADE)

class Post(models.Model):
    POST_STATUS = [
        ('draft', 'پیش‌نویس'),
        ('pending', 'در انتظار تایید'),
        ('published', 'منتشر شده'),
        ('rejected', 'رد شده'),
    ]
    
    POST_TYPES = [
        ('article', 'مقاله'),
        ('news', 'اخبار'),
        ('tutorial', 'آموزشی'),
        ('discount', 'تخفیف'),
        ('promotion', 'پرو موشن'),
    ]
    
    SCOPE_CHOICES = [
        ('internal', 'داخلی'),
        ('external', 'خارجی'),
    ]
    
    image = models.ImageField(upload_to='blog/', default='blog/default.jpg')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    editors = models.ManyToManyField(User, blank=True, related_name='editable_posts', verbose_name='ویراستاران')
    title = models.CharField(max_length=255)
    content = models.TextField()
    counted_views = models.IntegerField(default=0)
    tags = TaggableManager(through=TaggedPost, blank=True)   
    categories = models.ManyToManyField(Category, related_name='posts')
    
    # تغییر status به CharField با وضعیت‌های مختلف
    status = models.CharField(max_length=10, choices=POST_STATUS, default='draft', verbose_name='وضعیت')
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='article', verbose_name='نوع پست')
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default='internal', verbose_name='حوزه')
    has_discount = models.BooleanField(default=False, verbose_name='تخفیف دارد')
    discount_percentage = models.IntegerField(default=0, verbose_name='درصد تخفیف')
    
    published_date = models.DateTimeField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    # فیلدهای سئو
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان متا')
    meta_description = models.TextField(max_length=300, blank=True, verbose_name='توضیحات متا')
    
    # فیلدهای بررسی
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_posts', verbose_name='تایید شده توسط')
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تایید')
    
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = 'پست ها'
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['author', 'created_date']),
        ]
    
    def __str__(self):
        return "{} - {}".format(self.title, self.id)
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        elif self.status != 'published':
            self.published_date = None
            
        # اگر وضعیت به published تغییر کرد و approved_by نداریم، خودکار تایید شود
        if self.status == 'published' and not self.approved_by:
            self.approved_by = self.author
            self.approved_date = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:single', kwargs={'pid': self.id})
    
    def excerpt(self, words=25):
        plain_text = strip_tags(self.content)
        return Truncator(plain_text).words(words)
    
    def excerpt_chars(self, chars=100):
        plain_text = strip_tags(self.content)
        if len(plain_text) > chars:
            return plain_text[:chars] + '...'
        return plain_text
    
    def comments_count(self):
        return self.comments.filter(approved=True).count()
    
    def is_accessible_by(self, user):
        """بررسی دسترسی کاربر به پست"""
        if self.status == 'published':
            return True
        if user.is_authenticated:
            return (user.is_superuser or 
                   user == self.author or 
                   user in self.editors.all() or
                   user.groups.filter(name='Content Managers').exists())
        return False
    
    def can_edit(self, user):
        """بررسی امکان ویرایش پست توسط کاربر"""
        if not user.is_authenticated:
            return False
        return (user.is_superuser or 
               user == self.author or 
               user in self.editors.all() or
               user.groups.filter(name='Content Managers').exists())
    
    def can_delete(self, user):
        """بررسی امکان حذف پست توسط کاربر"""
        if not user.is_authenticated:
            return False
        return user.is_superuser or user == self.author
    
    @classmethod
    def get_accessible_posts(cls, user):
        """دریافت پست‌های قابل دسترسی برای کاربر"""
        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='Content Managers').exists():
                return cls.objects.all()
            return cls.objects.filter(
                models.Q(status='published') |
                models.Q(author=user) |
                models.Q(editors=user)
            ).distinct()
        return cls.objects.filter(status='published')
    
    @classmethod
    def get_featured_posts(cls, limit=5):
        return cls.objects.filter(status='published').order_by('-counted_views')[:limit]
    
    @classmethod
    def get_recent_posts(cls, limit=5):
        return cls.objects.filter(status='published').order_by('-published_date')[:limit]

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='پست')
    name = models.CharField(max_length=255, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    subject = models.CharField(max_length=255, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    approved = models.BooleanField(default=False, verbose_name='تأیید شده')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        indexes = [
            models.Index(fields=['post', 'approved', 'created_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def get_short_message(self):
        if len(self.message) > 50:
            return self.message[:50] + "..."
        return self.message