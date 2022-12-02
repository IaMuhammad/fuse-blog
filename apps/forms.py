from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput

from apps.models import CustomUser, Coment, Blog


class RegisterForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.data['confirm_password']
        if confirm_password != password:
            raise ValidationError('Parolni takshiring!')
        return make_password(password)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password', 'phone', 'email')


class LoginForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        if not CustomUser.objects.filter(username=username):
            raise ValidationError('username yoki parol xato kiritilgan!')
        return super().clean()

    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class UpdateForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))
    old_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.data['confirm_password']
        if confirm_password != password:
            raise ValidationError('Parolni takshiring!')
        return make_password(password)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password', 'confirm_password', 'phone', 'email')

    def __int__(self):
        self.fields['password'].required = False
        self.fields['confirm_password'].required = False


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        exclude = ('created_at',)

