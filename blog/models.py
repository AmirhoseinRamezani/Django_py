from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=150)
    
    def __str__(self):
        return self.name
    
class Post(models.Model):
    image = models.ImageField(upload_to='blog/',default='blog/default.jpg')
    author = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    counted_views = models.IntegerField(default=0)
    tags = TaggableManager()
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
    
    def get_absolute_url(self):
        return reverse('blog:single' ,kwargs={'pid':self.id})
