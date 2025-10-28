from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
import os


def user_profile_image_path(instance, filename):
    """مسیر ذخیره‌سازی تصویر پروفایل"""
    ext = filename.split('.')[-1]
    filename = f"profile_{instance.user.username}_{instance.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('profile_images', filename)


class UserLevel(models.TextChoices):
    NORMAL = 'normal', 'کاربر معمولی'
    WRITER = 'writer', 'نویسنده'
    ADMIN = 'admin', 'ادمین سایت'


class EducationLevel(models.TextChoices):
    DIPLOMA = 'diploma', 'دیپلم'
    ASSOCIATE = 'associate', 'کاردانی'
    BACHELOR = 'bachelor', 'کارشناسی'
    MASTER = 'master', 'کارشناسی ارشد'
    PHD = 'phd', 'دکتری'


class UserProfile(models.Model):
    # ارتباط با کاربر
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='کاربر'
    )
    
    # اطلاعات اصلی پروفایل
    bio = models.TextField(
        max_length=1000, 
        blank=True, 
        verbose_name='بیوگرافی',
        help_text='حداکثر ۱۰۰۰ کاراکتر'
    )
    
    user_level = models.CharField(
        max_length=10,
        choices=UserLevel.choices,
        default=UserLevel.NORMAL,
        verbose_name='سطح دسترسی'
    )
    
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        verbose_name='تصویر پروفایل',
        blank=True,
        null=True,
        help_text='تصویر با ابعاد 200x200 پیکسل مناسب است'
    )
    
    # اطلاعات شخصی
    birth_date = models.DateField(
        verbose_name='تاریخ تولد', 
        blank=True, 
        null=True,
        help_text='فرمت: YYYY-MM-DD'
    )
    
    phone_number = models.CharField(
        max_length=15, 
        verbose_name='شماره تلفن', 
        blank=True, 
        null=True,
        help_text='مثال: 09123456789'
    )
    
    # اطلاعات حرفه‌ای
    job_title = models.CharField(
        max_length=100, 
        verbose_name='عنوان شغلی', 
        blank=True, 
        null=True
    )
    
    company = models.CharField(
        max_length=100, 
        verbose_name='شرکت/سازمان', 
        blank=True, 
        null=True
    )
    
    # اطلاعات تحصیلی
    education_level = models.CharField(
        max_length=20,
        choices=EducationLevel.choices,
        verbose_name='سطح تحصیلات',
        blank=True,
        null=True
    )
    
    field_of_study = models.CharField(
        max_length=100, 
        verbose_name='رشته تحصیلی', 
        blank=True, 
        null=True
    )
    
    # شبکه‌های اجتماعی
    website = models.URLField(
        verbose_name='وبسایت شخصی', 
        blank=True, 
        null=True,
        help_text='آدرس کامل وبسایت'
    )
    
    github = models.URLField(
        verbose_name='GitHub', 
        blank=True, 
        null=True,
        help_text='آدرس پروفایل GitHub'
    )
    
    linkedin = models.URLField(
        verbose_name='LinkedIn', 
        blank=True, 
        null=True,
        help_text='آدرس پروفایل LinkedIn'
    )
    
    twitter = models.URLField(
        verbose_name='Twitter', 
        blank=True, 
        null=True,
        help_text='آدرس پروفایل Twitter'
    )
    
    instagram = models.URLField(
        verbose_name='Instagram', 
        blank=True, 
        null=True,
        help_text='آدرس پروفایل Instagram'
    )
    
    # متادیتا
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    updated_date = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل کاربران'
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['user_level']),
            models.Index(fields=['created_date']),
        ]
    
    def __str__(self):
        return f"پروفایل {self.user.username} - {self.get_user_level_display()}"

    def clean(self):
        """اعتبارسنجی داده‌ها"""
        errors = {}
        
        # اعتبارسنجی شماره تلفن
        if self.phone_number and not self.phone_number.isdigit():
            errors['phone_number'] = 'شماره تلفن باید فقط شامل اعداد باشد'
        
        # اعتبارسنجی تاریخ تولد
        if self.birth_date and self.birth_date > timezone.now().date():
            errors['birth_date'] = 'تاریخ تولد نمی‌تواند در آینده باشد'
        
        if errors:
            raise ValidationError(errors)

    def get_age(self):
        """محاسبه سن کاربر"""
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            
            # بررسی اینکه آیا تولد امسال گذشته یا نه
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            
            return age
        return None

    def get_full_name(self):
        """نام کامل کاربر"""
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username

    def get_social_links(self):
        """دریافت لینک‌های شبکه‌های اجتماعی"""
        social_links = {}
        
        if self.website:
            social_links['website'] = self.website
        if self.github:
            social_links['github'] = self.github
        if self.linkedin:
            social_links['linkedin'] = self.linkedin
        if self.twitter:
            social_links['twitter'] = self.twitter
        if self.instagram:
            social_links['instagram'] = self.instagram
            
        return social_links

    def has_complete_profile(self):
        """بررسی کامل بودن پروفایل"""
        required_fields = [
            self.bio,
            self.profile_image,
            self.job_title,
        ]
        return all(required_fields)

    def get_profile_completion_percentage(self):
        """درصد تکمیل پروفایل"""
        fields_to_check = [
            'bio', 'profile_image', 'job_title', 'company',
            'education_level', 'field_of_study', 'phone_number'
        ]
        
        completed = 0
        for field in fields_to_check:
            if getattr(self, field):
                completed += 1
        
        return int((completed / len(fields_to_check)) * 100)

    @property
    def display_name(self):
        """نام نمایشی کاربر"""
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.username

    @property
    def is_writer(self):
        """آیا کاربر نویسنده است؟"""
        return self.user_level == UserLevel.WRITER

    @property
    def is_admin(self):
        """آیا کاربر ادمین است؟"""
        return self.user_level == UserLevel.ADMIN

    def save(self, *args, **kwargs):
        """ذخیره پروفایل با مدیریت تصویر قدیمی"""
        # حذف تصویر قدیمی هنگام آپلود تصویر جدید
        if self.pk:
            try:
                old_profile = UserProfile.objects.get(pk=self.pk)
                if (old_profile.profile_image and 
                    old_profile.profile_image != self.profile_image and
                    os.path.isfile(old_profile.profile_image.path)):
                    old_profile.profile_image.delete(save=False)
            except (UserProfile.DoesNotExist, ValueError):
                pass
        
        # اعتبارسنجی قبل از ذخیره
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """حذف پروفایل با مدیریت فایل تصویر"""
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                self.profile_image.delete(save=False)
        super().delete(*args, **kwargs)


# سیگنال‌ها برای ایجاد و به‌روزرسانی خودکار پروفایل
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ایجاد پروفایل به صورت خودکار هنگام ایجاد کاربر جدید"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ذخیره پروفایل هنگام به‌روزرسانی کاربر"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


# مدیر مدل برای مدیریت بهتر در ادمین
class UserProfileManager(models.Manager):
    def writers(self):
        """دریافت تمام نویسندگان"""
        return self.filter(user_level=UserLevel.WRITER)
    
    def admins(self):
        """دریافت تمام ادمین‌ها"""
        return self.filter(user_level=UserLevel.ADMIN)
    
    def active_users(self):
        """دریافت کاربران فعال"""
        return self.filter(user__is_active=True)
    
    def get_complete_profiles(self, threshold=70):
        """دریافت پروفایل‌های با درصد تکمیل بالا"""
        complete_profiles = []
        for profile in self.all():
            if profile.get_profile_completion_percentage() >= threshold:
                complete_profiles.append(profile)
        return complete_profiles


# اضافه کردن مدیر سفارشی به مدل
UserProfile.add_to_class('objects', UserProfileManager())