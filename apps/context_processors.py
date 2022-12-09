from datetime import datetime, timedelta

from django.db.models import Q, Count

from apps.models import Category, Blog, BlogViewing


def context_category(request):
    return {
        'categories': Category.objects.all()
    }


def context_blog(request):
    return {
        'blogs': Blog.objects.filter(is_active=Blog.Active.active).order_by('created_at')
    }


def context_best(request):
    return {
        'bests': Blog.objects.filter(is_active=Blog.Active.active).order_by('created_at')[:3]
    }

def context_trending_posts(request):
    last = datetime.now() - timedelta(days=30)
    blogs_id = BlogViewing.objects.filter(viewed_at_date__gt=last).values_list('blog_id', 'viewed_at_date').annotate(
            count=Count('blog_id')).order_by('-count', '-viewed_at_date')[:5]

    blogs = Blog.objects.filter(id__in=[i[0] for i in blogs_id])
    return {
        'trending_posts' : blogs
        # 'trending_posts' : ''
    }