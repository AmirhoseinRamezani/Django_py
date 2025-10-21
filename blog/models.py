from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import Truncator


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
# مدل میانی سفارشی برای تگ‌ها
class TaggedPost(TaggedItemBase):
    content_object = models.ForeignKey('Post', on_delete=models.CASCADE)

class Post(models.Model):
    
    image = models.ImageField(upload_to='blog/',default='blog/default.jpg')
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    counted_views = models.IntegerField(default=0)
    tags = TaggableManager(through=TaggedPost, blank=True)   
    categories = models.ManyToManyField(Category, related_name='posts')
    status = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True)
    created_date =models.DateTimeField(auto_now_add=True)
    updated_date =models.DateTimeField(auto_now=True)
    
    # When we define attributes for an object inside a class,
    # these attributes are defined as general and are implemented throughout the program.
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = 'پست ها'
    def __str__(self):
        return "{} - {}".format(self.title,self.id)
    
    # def snippets(self):
    #     return self.content
    def save(self, *args, **kwargs):
        if self.status and not self.published_date:
            self.published_date = timezone.now()
        elif not self.status:
            self.published_date = None
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('blog:single' ,kwargs={'pid':self.id})

    def excerpt(self, words=25):
        """متن خلاصه بدون HTML"""
        plain_text = strip_tags(self.content)
        return Truncator(plain_text).words(words)
    
    def excerpt_chars(self, chars=100):
        """متن خلاصه بر اساس کاراکتر"""
        plain_text = strip_tags(self.content)
        if len(plain_text) > chars:
            return plain_text[:chars] + '...'
        return plain_text