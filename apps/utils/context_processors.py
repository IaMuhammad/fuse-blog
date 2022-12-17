from datetime import datetime, timedelta

from django.db.models import Count

from apps.models import Category, Blog, BlogViewing


def context_category(request):
    return {
        'categories': Category.objects.all()
    }


def context_blog(request):
    return {
        'blogs': Blog.active.order_by('-created_at')
    }


def context_best(request):
    return {
        'bests': Blog.active.order_by('created_at')[:3]
    }


def context_trending_posts(request):
    last = datetime.now() - timedelta(days=30)
    blogs = BlogViewing.objects.filter(viewed_date__gt=last).values('blog_id', 'blog__title', 'blog__slug',
                                                                    'blog__description', 'blog__main_picture',
                                                                    'blog__created_at', 'blog__author').annotate(
        count=Count('blog_id'))[:5]

    return {
        'trending_posts': blogs
    }
