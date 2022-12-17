from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, FormView

from apps.forms import RegisterForm, LoginForm, BlogForm, UpdateUserForm, ContactForm, CommentForm, ForgotPasswordForm, \
    ChangePasswordForm
from apps.models import Blog, Category, CustomUser, Comment, Message, BlogViewing
from apps.utils.make_pdf import render_to_pdf
from apps.utils.tasks import send_to_gmail
# from apps.utils import senf_mail_func
# from apps.utils.tasks import test_func
from apps.utils.token import account_activation_token


class LoginMixin:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main_view')
        return super().get(request, *args, **kwargs)


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        blog = Blog.objects.filter(slug=kwargs.get('slug')).first()
        data = {
            'blog': blog,
        }
        pdf = render_to_pdf('apps/make_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


# Create your views here.
class MainPageView(ListView):
    model = Blog
    template_name = 'apps/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['news'] = Blog.objects.order_by('created_at', 'title')[:5]

        return context


class AboutPageView(TemplateView):
    template_name = 'apps/about.html'


class ContactPageVIew(CreateView):
    template_name = 'apps/contact.html'
    model = Message
    fields = ('author', 'message')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BlogListView(ListView):
    template_name = 'apps/blog-category.html'
    paginate_by = 4
    model = Blog

    # queryset = Category.objects.order_by('name')
    # context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context['news'] = Blog.active.all()
        context['categories_list'] = Category.objects.all()
        context['categories'] = Category.objects.order_by('name')
        s = self.request.path.split('/')[-1]
        obj = Category.objects.filter(slug=s).first()

        if obj:
            context['path'] = obj.name
            if obj.name != 'all':
                context['blogs'] = Blog.active.filter(category__id=obj.id)

        elif s != 'all':
            context['blogs'] = None
            context['path'] = s
        return context


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

    # def get_queryset(self):
    #     Blog.objects.filter(slug=self.kwargs.get('slug')).update(view=F('view') + 1)
    #     return super().get_queryset()

    def post(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        blog = get_object_or_404(Blog, slug=slug)
        data = {
            'blog': blog,
            'author': request.user,
            'coment': request.POST.get('message')
        }
        form = self.form_class(data)
        if form.is_valid():
            form.save()

        # blog =
        return redirect('post_view', slug)

    def form_valid(self, form):
        return super().form_valid(form)


class AddBlogPageView(CreateView):
    form_class = BlogForm
    model = Blog
    template_name = 'apps/add_post.html'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.title = form.data.get('title')
        obj.save()

        return redirect('post_view', obj.slug)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SendMessageAdmin(CreateView, LoginRequiredMixin):
    form_class = ContactForm
    template_name = 'apps/contact.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('contact_view')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return redirect('contact_view', form.instance.author.username)


class CustomLogoutView(LogoutView):
    # form_class = LoginForm()
    # template_name = 'auth/auth/login.html'
    next_page = reverse_lazy('main_view')


class FooterView(ListView):
    template_name = 'apps/parts/footer.html'
    queryset = Blog.objects.order_by('created_at')[:3]
    context_object_name = 'footer_blogs'
    model = Blog

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        # context['footers'] = Blog.objects.order_by('created_at')
        return context


class BLogUpdateView(UpdateView, LoginRequiredMixin):
    model = Blog
    fields = ('title', 'description', 'category', 'main_pic')
    success_url = reverse_lazy('main_view')


class RegisterPageView(LoginMixin, CreateView):
    form_class = RegisterForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('main_view')

    def form_valid(self, form):
        user = form.save()
        if user:
            user = authenticate(username=user.username, password=user.password)
            if user:
                login(self.request, user)
        current_site = get_current_site(self.request)
        send_to_gmail.apply_async(args=[form.data.get('email'), current_site.domain, 'activate'])
        return super().form_valid(form)

    # def form_valid(self, form):
    #     form.instance.is_active = False
    #     con = {'username': form.data['username'],
    #            'email': form.data['email']}
    #     user = form.save()
    #     code = send_message(con)
    #     if user is not None:
    #         login(self.request, user)
    #     return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ActivateEmailView(TemplateView):
    template_name = 'auth/confirm-mail.html'

    def get(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=uid)
        except Exception as e:
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message="Your account successfully activated!"
            )
            return redirect('main_view')
        else:
            return HttpResponse('Activation link is invalid!')


class LoginPageView(LoginMixin, LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    next_page = reverse_lazy('main_view')

    # def get(self, request, *args, **kwargs):
    #     if request.method == 'POST':
    #         forms =
    #     return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = LoginForm
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UpdateUserForm
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'auth/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_blogs'] = Blog.objects.filter(author=self.request.user).order_by('-created_at')
        return context

    def form_valid(self, form):
        self.object = CustomUser.objects.get(username=self.request.user)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object=self.object, form=form)

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return redirect('user_update_view', self.object.username)


class ChangePasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        username = request.user.username
        user = request.user
        form = ChangePasswordForm(request.POST, initial={'request': request})
        if form.is_valid():
            form.save(request.user)
            password = form.data.get('new_password')
            user = authenticate(username=username, password=password)
            login(request, user)
        return redirect('user_update_view', user.username)


class VerifyView(TemplateView):
    template_name = 'auth/verify.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ForgotPasswordView(FormView):
    template_name = 'auth/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('login_view')

    def form_valid(self, form):
        current_site = get_current_site(self.request)
        send_to_gmail.apply_async(args=[form.data.get('email'), current_site.domain, 'reset'])
        return super().form_valid(form)


class ResetPasswordView(TemplateView):
    template_name = 'auth/reset_password.html'

    def get_user(self, uid, token):
        uid = force_str(urlsafe_base64_decode(uid))
        user = CustomUser.objects.get(id=uid)
        return user, user and account_activation_token.check_token(user, token)

    def get(self, request, *args, **kwargs):
        user, is_valid = self.get_user(**kwargs)
        if not is_valid:
            return HttpResponse('Link not found')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user, is_valid = self.get_user(**kwargs)
        if is_valid:
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('login_view')
        return HttpResponse('Link not found')


class ConfirmPasswordView(TemplateView):
    template_name = 'auth/confirm_password.html'
