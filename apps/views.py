from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, UpdateView, FormView

from apps.forms import RegisterForm, LoginForm, BlogForm, UpdateUserForm
from apps.models import Blog, Category, CustomUser, Coment, Message


# Create your views here.
class MainPageView(ListView):
    model = Blog
    template_name = 'apps/index.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['bests'] = Blog.objects.all()[:2]
        context['news'] = Blog.objects.order_by('created_at', 'title')[:5]

        return context


class BlogListView(ListView):
    template_name = 'apps/blog-category.html'
    paginate_by = 2
    model = Blog
    queryset = Category.objects.order_by('name')
    context_object_name = 'categories'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['news'] = Blog.objects.order_by('created_at', 'title')[:5]
        context['categories_list'] = Category.objects.all()
        s = self.request.path.split('/')[-1]
        obj = Category.objects.filter(slug=s).first()

        if obj:
            context['path'] = obj.name
            if obj.name != 'all':
                context['blogs'] = Blog.objects.filter(category__id=obj.id)

        elif s != 'all':
            context['blogs'] = None
            context['path'] = s
        return context


class CreateCommentBLog(CreateView, LoginRequiredMixin):
    model = Coment
    fields = '__all__'
    template_name = 'apps/post.html'
    success_url = reverse_lazy('post_view')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog = self.request.path.split('/')[-1]
        return super().form_valid(form)



class AboutPageView(TemplateView):
    template_name = 'apps/about.html'


class ContactPageVIew(CreateView):
    template_name = 'apps/contact.html'
    model = Message
    fields = ('author', 'message')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class SendMessageAdmin(CreateView, LoginRequiredMixin):
    model = Message
    fields = '__all__'
    template_name = 'apps/contact.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    success_url = reverse_lazy('contact_view')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.blog = self.request.path.split('/')[-1]
        return super().form_valid(form)


class BlogPageView(DetailView, FormView):
    model = Blog
    form_class = BlogForm
    template_name = 'apps/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog'] = Blog.objects.filter(slug=self.request.path.split('/')[-1]).first()
        context['blog_category'] = context['blog'].category.all()
        return context

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        # blog =
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


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


class RegisterPageView(CreateView):
    form_class = RegisterForm
    template_name = 'auth/auth/register.html'
    success_url = reverse_lazy('main_view')

    def form_valid(self, form):
        form.instance.is_active = False
        con = {'username': form.data['username'],
               'email': form.data['email']}
        user = form.save()
        code = send_message(con)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)


class LoginPageView(LoginView):
    form_class = LoginForm
    template_name = 'auth/auth/login.html'
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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UpdateUserForm
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'auth/auth/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['user_blogs'] = Blog.objects.filter(author=self.request.user)
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

    def form_invalid(self, form):
        return super().form_invalid(form)


class VerifyView(TemplateView):
    template_name = 'auth/auth/verify.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AddPost(TemplateView):
    template_name = 'apps/add_post.html'


def send_message(context):
    import smtplib
    import ssl
    from email.message import EmailMessage

    email_receiver = context['email']
    username = context['username']

    email_sender = 'muhammedovabubakir03@gmail.com'
    email_password = 'eeowgnatobtdqggm'
    email_receiver = context['email']
    username = context['username']
    subject = 'YOUR VERIFICATION CODE'
    body = f"""
                    Hello {username}!!!
                You registered an account on {0000}, before being able to use your account you need to verify that this is.
                Type this code to field that under this message  

                Abu Bakir Muhammedov!
                """
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
