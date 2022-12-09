from datetime import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, SlugField, CharField, ForeignKey, CASCADE, DateField, TextField, ImageField, \
    SET_NULL, ManyToManyField, SET_DEFAULT, EmailField, TextChoices, DateTimeField, PROTECT
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email = EmailField(max_length=255, unique=True)
    phone = CharField(max_length=255, unique=True, null=True, blank=True)
    birthday = DateField(auto_now=True)
    description = TextField(null=True, blank=True)
    majority = CharField(max_length=255, null=True, blank=True)
    photo = ImageField(default='users/defaultuser.png')

    # class Meta:
    #     verbose_name = 'Foydalanuvchi'
    #     verbose_name_plural = 'Foydalanuvchilar'

    @property
    def years_old(self):
        return datetime.now().year - self.birthday.year

    @property
    def birthday_date(self):
        return f'{self.birthday.year}-{self.birthday.month}-{self.birthday.day}'


class Category(Model):
    name = CharField(max_length=255)
    picture = ImageField(upload_to='%m', null=True, blank=True)
    slug = SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    @property
    def blog_count(self):
        return self.blog_set.filter(is_active=Blog.Active.active).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            while Blog.objects.filter(slug=self.slug).exists():
                slug = Blog.objects.filter(slug=self.slug).first().slug
                if '-' in slug:
                    try:
                        if slug.split('-')[-1] in self.name:
                            self.slug += '-1'
                        else:
                            self.slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                    except:
                        self.slug = slug + '-1'
                else:
                    self.slug += '-1'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Blog(Model):
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Bloglar'

    class Active(TextChoices):  # A subclass of Enum
        active = 'active', _('active')
        canceled = 'canceled', _('canceled')
        pending = 'pending', _('pending')

    title = CharField(max_length=255, null=True, blank=True)
    author = ForeignKey('apps.CustomUser', SET_NULL, null=True, blank=True)
    category = ManyToManyField(Category)
    description = RichTextUploadingField()
    slug = SlugField(max_length=255, unique=True)
    main_picture = ImageField(upload_to='%m', null=True, blank=True)
    created_at = DateField(auto_now=True)
    is_active = CharField(max_length=8, choices=Active.choices, default=Active.pending)

    def status_button(self):
        if self.is_active == Blog.Active.pending:
            return format_html(
                f'''<a href="active/{self.id}" class="button">Active</a>
                        <a href="canceled/{self.id}" class="button">canceled</a>'''
            )
        elif self.is_active == Blog.Active.active:
            return format_html(
                f'''<a style="color: green; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlangan</a>''')

        return format_html(
            f'''<a style="color: red; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlanmagan</a>''')

    @property
    def comment_count(self):
        return self.comment_set.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            while Blog.objects.filter(slug=self.slug).exists():
                slug = Blog.objects.filter(slug=self.slug).first().slug
                if '-' in slug:
                    try:
                        if slug.split('-')[-1] in self.title:
                            self.slug += '-1'
                        else:
                            self.slug = '-'.join(slug.split('-')[:-1]) + '-' + str(int(slug.split('-')[-1]) + 1)
                    except:
                        self.slug = slug + '-1'
                else:
                    self.slug += '-1'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Coment(Model):
    coment = TextField()
    author = ForeignKey('apps.CustomUser', SET_DEFAULT, default=0)
    blog = ForeignKey('apps.Blog', CASCADE, related_name='comment_set')
    created_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Komentariya'
        verbose_name_plural = 'Komentariyalar'

    def __str__(self):
        return f'{self.author} -> {self.coment[:20]}'

class BlogViewing(Model):
    blog = ForeignKey(Blog, CASCADE)
    viewed_at = DateTimeField(auto_now=True)
    viewed_at_date = DateField(auto_now=True)

    def __str__(self):
        return f'{self.blog_id}'


class Message(Model):
    author = ForeignKey(CustomUser, on_delete=CASCADE)
    message = TextField()
    written_at = DateTimeField(auto_now=True)
