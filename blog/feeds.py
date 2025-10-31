from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from blog.models import Post

class LatestEntriesFeed(Feed):
    title = "Blog Newest Posts"
    link = "/rss/feed"
    description = "Latest posts from our blog" 
    description_template = "feeds/post-content.html"
    
    def items(self):
        # ✅ اصلاح شده: استفاده از status='published'
        return Post.objects.filter(
            status='published'
        ).select_related('author').prefetch_related('categories', 'tags')[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_link(self, item):
        return reverse('blog:single', args=[item.id])
    
    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username
    
    def item_pubdate(self, item):
        return item.published_date
    
    def item_updateddate(self, item):
        return item.updated_date

class AtomSiteNewsFeed(LatestEntriesFeed):
    feed_type = Atom1Feed
    subtitle = LatestEntriesFeed.description