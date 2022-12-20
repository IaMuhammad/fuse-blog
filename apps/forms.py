from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, PasswordInput, EmailField, Form

from apps.models import CustomUser, Comment, Blog, Message


class RegisterForm(ModelForm):
    confirm_password = CharField(widget=PasswordInput(attrs={"autocomplete": "current-password"}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'password', 'phone', 'email')

    def clean_password(self):
        new_password = self.cleaned_data['password']
        re_new_password = self.data['confirm_password']
        if re_new_password != new_password:
            raise ValidationError('Parolni takshiring!')
        return make_password(new_password)

    # @atomic
    # def save(self):
    #     user = CustomUser.objects.create_user(
    #         username=self.cleaned_data.get('username'),
    #         email=self.cleaned_data.get('email'),
    #         is_active=False
    #     )
    #     user.set_password(self.cleaned_data.get('password'))
    #     user.save()


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


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ()


class ContactForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


class ForgotPasswordForm(Form):
    email = EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError('This profile is not exist!')
        return email

    class Meta:
        model = CustomUser
        fields = ('email',)


class ChangePasswordForm(Form):
    password = CharField(max_length=255)
    new_password = CharField(max_length=255)
    confirm_new_password = CharField(max_length=255)

    def clean(self):
        return super().clean()

    def clean_password(self):
        user = self.inictial['request'].user
        password = self.cleaned_data.get('password')
        if not user.check_password(password):
            raise ValidationError('Eski parol xato')
        return password

    def clean_confirm_new_password(self):
        new_password = self.data.get('new_password')
        confirm_password = self.data.get('confirm_new_password')
        if new_password != confirm_password:
            raise ValidationError('Parol xato!')
        return new_password

    def save(self, user):
        new_password = self.cleaned_data.get('new_password')
        user.set_password(new_password)
        user.save()
