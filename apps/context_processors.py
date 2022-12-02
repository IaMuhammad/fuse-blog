from apps.models import Category, Blog


def context_category(request):
    return {
        'categories': Category.objects.all()
    }


def context_blog(request):
    return {
        'blogs': Blog.objects.all()
    }
