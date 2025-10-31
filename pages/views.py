# pages/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.db.models import Q
from .models import Page
from tours.models import Tour
from blog.models import Post
from django.utils import timezone
from django.core.cache import cache

class PageListView(ListView):
    model = Page
    template_name = 'pages/page_list.html'
    context_object_name = 'pages'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Page.objects.filter(status='published')
        
        # فیلتر بر اساس نوع صفحه
        page_type = self.request.GET.get('type')
        if page_type:
            queryset = queryset.filter(page_type=page_type)
        
        # فیلتر بر اساس دسترسی
        if not self.request.user.is_staff:
            queryset = queryset.filter(access_level='public')
        
        return queryset.order_by('-published_date')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        cache_key = 'featured_tours_cache'
        featured_tours = cache.get(cache_key)
        
        if not featured_tours:
            try:
                featured_tours = Tour.objects.filter(
                    is_active=True,
                    is_featured=True,
                    departure_datetime__gte=timezone.now()
                ).select_related('category', 'departure_transportation')[:5]
                # cache برای 1 ساعت
                cache.set(cache_key, featured_tours, 3600)
            except Exception as e:
                featured_tours = []
        
        context['featured_tours'] = featured_tours
        context['page_types'] = dict(Page.PAGE_TYPES)
        
    
        # ✅ الگوریتم بهینه: استفاده از select_related بدون only
        try:
            context['featured_tours'] = Tour.objects.filter(
                is_active=True,
                is_featured=True,
                departure_datetime__gte=timezone.now()
            ).select_related('category', 'departure_transportation')[:5]
        except Exception as e:
            # در صورت خطا، لیست خالی برگردان
            context['featured_tours'] = []
            print(f"Error loading featured tours: {e}")
        
        context['featured_tours'] = featured_tours
        context['page_types'] = dict(Page.PAGE_TYPES)
        return context

class PageDetailView(DetailView):
    model = Page
    template_name = 'pages/page_detail.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        # ✅ الگوریتم بهینه: prefetch_related برای بخش‌ها و لینک‌ها
        return Page.objects.prefetch_related('sections', 'links')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # بررسی دسترسی
        if not obj.is_accessible_by(self.request.user):
            raise Http404("این صفحه موجود نیست")
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object
        
        # ✅ الگوریتم بهینه: استفاده از select_related بدون only
        try:
            context['upcoming_tours'] = Tour.objects.filter(
                is_active=True,
                departure_datetime__gte=timezone.now()
            ).select_related('category').order_by('departure_datetime')[:6]
        except:
            context['upcoming_tours'] = []
        
        # ✅ الگوریتم بهینه: استفاده از select_related برای پست‌ها
        try:
            context['discount_posts'] = Post.objects.filter(
                status=True
            ).filter(
                Q(categories__name__icontains='تخفیف') | 
                Q(tags__name__icontains='تخفیف')
            ).distinct().select_related('author').order_by('-published_date')[:4]
        except:
            context['discount_posts'] = []
        
        # ✅ الگوریتم بهینه: صفحات مرتبط
        context['related_pages'] = Page.objects.filter(
            page_type=page.page_type,
            status='published',
            access_level='public'
        ).exclude(id=page.id)[:4]
        
        # ✅ الگوریتم بهینه: تورها و پست‌های مرتبط
        context['related_tours'] = page.related_tours.filter(
            is_active=True
        ).select_related('category')[:6]
        
        context['related_posts'] = page.related_posts.filter(
            status=True
        ).select_related('author')[:6]
        
        return context

def page_detail_by_type(request, page_type):
    """نمایش صفحات بر اساس نوع"""
    # ✅ الگوریتم بهینه: استفاده از select_related
    pages = Page.objects.filter(
        page_type=page_type,
        status='published'
    ).select_related('author')
    
    if not request.user.is_staff:
        pages = pages.filter(access_level='public')
    
    context = {
        'pages': pages.order_by('-published_date'),
        'page_type': page_type,
        'page_type_display': dict(Page.PAGE_TYPES).get(page_type, 'صفحات')
    }
    
    return render(request, 'pages/page_list_by_type.html', context)