from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, FormView

from apps.forms import RegisterForm, LoginForm, UpdateUserForm, ContactForm, ForgotPasswordForm, \
    ChangePasswordForm
from apps.models import Blog, CustomUser
from apps.utils.tasks import send_to_gmail
from apps.utils.token import account_activation_token


class LoginMixin:
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main_view')
        return super().get(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    # form_class = LoginForm()
    # template_name = 'auth/auth/login.html'
    next_page = reverse_lazy('main_view')


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

    def form_invalid(self, form):
        context = {
            'errors': form.errors,
        }
        return render(self.request, 'auth/register.html', context)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = LoginForm
        return context

    def form_invalid(self, form):
        context = {
            'errors': 'Please enter correct username and password. Note both fields may be case-sensitive.',
        }
        return render(self.request, 'auth/login.html', context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UpdateUserForm
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'auth/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        username = request.path.split('/')[-1]
        context['editable'] = username == request.user.username
        if context['editable']:
            context['edit_user'] = self.request.user
        else:
            context['edit_user'] = CustomUser.objects.get(username=username)
        context['user_blogs'] = Blog.active.filter(author__username=username)
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


