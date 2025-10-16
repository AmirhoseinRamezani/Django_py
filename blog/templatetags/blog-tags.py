from django import template
from blog.models import Post
from blog.models import Category
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

@register.inclusion_tag('blog/blog-post-categories.html')
def postcategories():
#     categories = Category.objects.annotate(
#         post_count=Count('post_category')  # Use the actual related_name
#     ).filter(
#         post_category__status=True  # Use the actual related_name
#     ).order_by('-post_count').distinct()
    
#     return {'categories': categories}
    posts = Post.objects.filter(status=1)
    categories = Category.objects.all()
    cat_dict = {}
    for name in categories:
        cat_dict[name] = posts.filter(categories=name).count()
        
    return{'categories':cat_dict}
# def postcategories(context):
#     request = context.get('request')
#     post_id = context.get('post_id')
    
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