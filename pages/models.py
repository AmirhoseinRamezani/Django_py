# pages/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from tours.models import Tour
from blog.models import Post

class Page(models.Model):
    PAGE_TYPES = [
        ('about', 'درباره ما'),
        ('service', 'خدمات'),
        ('policy', 'قوانین'),
        ('contact', 'تماس'),
        ('news', 'اخبار'),
        ('promotion', 'تخفیف‌ها'),
        ('tour_info', 'اطلاعات تورها'),
        ('custom', 'سفارشی'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
        ('archived', 'آرشیو شده'),
    ]
    
    ACCESS_LEVELS = [
        ('public', 'عمومی'),
        ('private', 'خصوصی - فقط ادمین‌ها'),
        ('premium', 'ویژه - کاربران خاص'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان صفحه')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='اسلاگ')
    
    # محتوای پیشرفته
    content = RichTextField(verbose_name='محتوا')
    excerpt = models.TextField(max_length=300, blank=True, verbose_name='چکیده')
    
    # تصاویر
    featured_image = models.ImageField(upload_to='pages/', blank=True, null=True, verbose_name='تصویر شاخص')
    thumbnail = models.ImageField(upload_to='pages/thumbnails/', blank=True, null=True, verbose_name='تصویر کوچک')
    
    # تنظیمات صفحه
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, default='custom', verbose_name='نوع صفحه')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='وضعیت')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public', verbose_name='سطح دسترسی')
    
    # نمایش
    show_in_menu = models.BooleanField(default=True, verbose_name='نمایش در منو')
    show_in_footer = models.BooleanField(default=False, verbose_name='نمایش در فوتر')
    show_featured = models.BooleanField(default=False, verbose_name='نمایش در صفحات ویژه')
    menu_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب در منو')
    
    # ارتباط با تورها و پست‌ها
    related_tours = models.ManyToManyField(
        'tours.Tour', 
        blank=True, 
        verbose_name='تورهای مرتبط',
        related_name='pages'
    )
    related_posts = models.ManyToManyField(
        'blog.Post', 
        blank=True, 
        verbose_name='پست‌های مرتبط',
        related_name='pages'
    )
    
    # سئو
    meta_title = models.CharField(max_length=200, blank=True, verbose_name='متا عنوان')
    meta_description = models.TextField(max_length=300, blank=True, verbose_name='متا توضیحات')
    meta_keywords = models.CharField(max_length=200, blank=True, verbose_name='کلمات کلیدی')
    
    # اطلاعات نویسنده
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='نویسنده')
    editors = models.ManyToManyField(
        User, 
        blank=True, 
        related_name='editable_pages',
        verbose_name='ویراستاران',
        help_text='کاربران مجاز برای ویرایش این صفحه'
    )
    
    # تاریخ‌ها
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    published_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انتشار')
    expiration_date = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ انقضا')
    
    class Meta:
        verbose_name = 'صفحه'
        verbose_name_plural = 'صفحات'
        ordering = ['menu_order', 'title']
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['page_type', 'show_in_menu']),
            models.Index(fields=['access_level', 'status']),
        ]
        permissions = [
            ('can_manage_pages', 'می‌تواند صفحات را مدیریت کند'),
            ('can_publish_pages', 'می‌تواند صفحات را منتشر کند'),
            ('can_edit_private_pages', 'می‌تواند صفحات خصوصی را ویرایش کند'),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})
    
    def is_published(self):
        """بررسی انتشار صفحه"""
        now = timezone.now()
        return (self.status == 'published' and 
                self.published_date is not None and
                (self.expiration_date is None or self.expiration_date > now))
    
    def is_accessible_by(self, user):
        """بررسی دسترسی کاربر به صفحه"""
        if self.access_level == 'public':
            return True
        elif self.access_level == 'private':
            return user.is_authenticated and user.is_staff
        elif self.access_level == 'premium':
            return user.is_authenticated and (user.is_staff or hasattr(user, 'premium_subscription'))
        return False
    
    def get_related_tours_display(self):
        """نمایش تورهای مرتبط"""
        return self.related_tours.filter(is_active=True)[:6]
    
    def get_related_posts_display(self):
        """نمایش پست‌های مرتبط"""
        return self.related_posts.filter(status=True)[:6]

    publish_to_blog = models.BooleanField(default=False, verbose_name='انتشار در بلاگ')
    blog_post = models.OneToOneField(
        'blog.Post', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='page_source',
        verbose_name='پست مرتبط در بلاگ'
    )
    
    def save(self, *args, **kwargs):
        from blog.models import Post
        
        is_new = self._state.adding
        
        super().save(*args, **kwargs)
        
        # اگر انتخاب شده که در بلاگ منتشر شود
        if self.publish_to_blog and self.status == 'published':
            if not self.blog_post:
                # ایجاد پست جدید در بلاگ
                blog_post = Post.objects.create(
                    title=self.title,
                    content=self.content,
                    excerpt=self.excerpt,
                    author=self.author,
                    status=True,
                    published_date=timezone.now(),
                    # سایر فیلدهای لازم...
                )
                self.blog_post = blog_post
                # ذخیره مجدد بدون فراخوانی save برای جلوگیری از حلقه
                super().save(update_fields=['blog_post'])
class PageSection(models.Model):
    """بخش‌های مختلف یک صفحه"""
    LAYOUT_CHOICES = [
        ('default', 'پیش‌فرض'),
        ('image_left', 'تصویر چپ'),
        ('image_right', 'تصویر راست'),
        ('full_width', 'تمام عرض'),
        ('columns_2', 'دو ستونه'),
        ('columns_3', 'سه ستونه'),
    ]
    
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name='عنوان بخش')
    content = RichTextField(verbose_name='محتوا')
    image = models.ImageField(upload_to='page-sections/', blank=True, null=True, verbose_name='تصویر')
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='default', verbose_name='طرح‌بندی')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        verbose_name = 'بخش صفحه'
        verbose_name_plural = 'بخش‌های صفحات'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.page.title} - {self.title}"

class PageLink(models.Model):
    """لینک‌های داخلی و خارجی در صفحه"""
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=100, verbose_name='عنوان لینک')
    url = models.CharField(max_length=500, verbose_name='آدرس')
    is_external = models.BooleanField(default=False, verbose_name='لینک خارجی')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        verbose_name = 'لینک صفحه'
        verbose_name_plural = 'لینک‌های صفحات'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.page.title} - {self.title}"