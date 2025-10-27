from django import template
from blog.models import Post,Category
from django.db.models import Count
# from django.db.models import Count,Sum

register = template.Library()

@register.simple_tag(name = 'totalposts')
def function():
    posts = Post.objects.filter(status=1).count()
    return posts

@register.inclusion_tag('blog/blog-popular-posts.html', name='latestposts')
def latestposts(arg=5):
    posts = Post.objects.filter(status=1).order_by('-published_date')[:arg]
    return {'posts':posts}

@register.inclusion_tag('blog/blog-post-categories.html', name='postcategories')
def post_categories():
    # روش بهینه‌شده با استفاده از annotate
    categories = Category.objects.annotate(
        post_count=Count('posts')
    ).filter(
        post_count__gt=0
    ).order_by('-post_count')
    
    # تبدیل به دیکشنری برای سازگاری با تمپلیت موجود
    cat_dict = {}
    for category in categories:
        cat_dict[category.name] = category.post_count
        
    return {'categories': cat_dict}
    
#     # اگر در صفحه سینگل هستیم و post_id وجود دارد
#     if post_id:
#         try:
#             current_post = Post.objects.get(id=post_id, status=1)
#             post_categories = current_post.categories.all()
            
#             cat_dict = {}
#             for category in post_categories:
#                 count = Post.objects.filter(status=1, categories=category).count()
#                 cat_dict[category] = count
            
#             return {
#                 'categories': cat_dict,
#                 'is_single_page': True
#             }
#         except Post.DoesNotExist:
        
#             posts = Post.objects.filter(status=1)
#             categories = Category.objects.all()
#             cat_dict = {}
#             for name in categories:
#                 cat_dict[name] = posts.filter(categories=name).count()
                
#             return{'categories':cat_dict}