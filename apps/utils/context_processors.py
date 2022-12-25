from datetime import datetime, timedelta

from django.db.models import Count

from apps.models import Category, Blog, BlogViewing, Site


def context_category(request):
    return {
        'categories': Category.objects.order_by('name')
    }


def context_blog(request):
    return {
        # 'blogs': Blog.active.order_by('-created_at')
    }


def context_best(request):
    return {
        'bests': Blog.active.order_by('created_at')[:3]
    }


def context_trending_posts(request):
    last = datetime.now() - timedelta(days=30)
    blogs = BlogViewing.objects.all().aggregate(Count('id'))

    return {
        'trending_posts': blogs
    }
def context_site_info(request):
    info = Site.objects.first()

    return {
        'info': info
    }