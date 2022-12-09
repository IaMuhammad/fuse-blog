from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput

from apps.models import CustomUser, Coment, Blog, Message


class RegisterForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    def clean_password(self):
        new_password = self.cleaned_data['password']
        re_new_password = self.data['confirm_password']
        if re_new_password != new_password:
            raise ValidationError('Parolni takshiring!')
        return make_password(new_password)

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


class UpdateUserForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'phone', 'email', 'description', 'photo')

    def __int__(self):
        # self.fields['first_name'].required = False
        # self.fields['last_name'].required = False
        self.fields['username'].required = False
        self.fields['phone'].required = False
        self.fields['password'].required = False
        self.fields['new_password'].required = False
        self.fields['re_new_password'].required = False
        self.fields['description'].required = False


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ('title', 'main_picture', 'category', 'description')
        exclude = ('created_at',)


class ComentForm(ModelForm):
    class Meta:
        model = Coment
        exclude = ()


class ContactForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
