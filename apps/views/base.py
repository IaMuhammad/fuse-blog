from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, FormView

from apps.forms import BlogForm, CommentForm, ContactForm
from apps.models import Blog, Category, Comment, BlogViewing
from apps.utils.make_pdf import render_to_pdf


class GeneratePdf(DetailView):
    template_name = 'apps/make_pdf.html'

    def get(self, request, *args, **kwargs):
        blog = Blog.objects.filter(slug=kwargs.get('slug')).first()
        data = {
            'blog': blog,
            'current_url': f"http://{self.request.headers['Host']}/blog/{blog.slug}",
            'download': f"http://{self.request.headers['Host']}/pdf/{blog.slug}"

        }
        pdf = render_to_pdf('apps/make_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class MainPageView(ListView):
    model = Blog
    template_name = 'apps/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['news'] = Blog.objects.order_by('created_at', 'title')[:5]

        return context


class AboutPageView(TemplateView):
    template_name = 'apps/about.html'


class BlogListView(ListView):
    template_name = 'apps/blog-category.html'
    queryset = Blog.active.all()
    context_object_name = 'blogs'
    paginate_by = 4

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['news'] = Blog.active.all()
        context['comment_count'] = Blog.active.all()
        context['path'] = self.request.path.split('/')[-1]
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.request.path.split('/')[-1]
        if category := Category.objects.filter(slug=slug):
            return qs.filter(category__slug=slug)
        return qs


class BlogPageView(FormView, DetailView):
    form_class = CommentForm
    queryset = Blog.objects.all()
    template_name = 'apps/post.html'

    def get_queryset(self):
        blog = Blog.objects.filter(slug=self.kwargs.get('slug')).first()
        BlogViewing.objects.create(blog_id=blog.id)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = Blog.objects.filter(slug=self.request.path.split('/')[-1]).first()
        context['blog_category'] = context['blog'].category.all()
        context['commentaries'] = Comment.objects.filter(blog_id=context['blog'].id)
        return context

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        blog = get_object_or_404(Blog, slug=slug)
        data = {
            'blog': blog,
            'author': request.user,
            'comment': request.POST.get('message')
        }
        form = self.form_class(data)
        if form.is_valid():
            form.save()

        return redirect('post_view', slug)


class ContactPageVIew(CreateView):
    form_class = ContactForm
    template_name = 'apps/contact.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('contact_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return redirect('contact_view', form.instance.author.username)

    def form_invalid(self, form):
        return super().form_invalid(form)


class AddBlogPageView(CreateView):
    form_class = BlogForm
    model = Blog
    template_name = 'apps/add_post.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.title = form.data.get('title')
        categories = form.cleaned_data.get('category').values_list('pk', flat=True)

        obj.save()
        print()
        obj.category.add(*categories)

        return redirect('post_view', obj.slug)


class BLogUpdateView(UpdateView, LoginRequiredMixin):
    model = Blog
    fields = ('title', 'description', 'category', 'main_pic')
    success_url = reverse_lazy('main_view')
