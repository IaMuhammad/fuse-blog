from datetime import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django import template
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, SlugField, CharField, ForeignKey, CASCADE, DateField, TextField, ImageField, \
    SET_NULL, ManyToManyField, EmailField, TextChoices, DateTimeField, Manager, BooleanField, JSONField
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.managers import UserManager

register = template.Library()


class Site(Model):
    name = CharField(max_length=255)
    picture = ImageField()
    about_us = TextField()
    social = JSONField(blank=True, null=True)
    adress = CharField(max_length=255)
    email = EmailField()
    phone = CharField(max_length=20)

    class Meta:
        verbose_name = 'Sayt haqida'
        verbose_name_plural = 'Sayt haqida'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    email = EmailField(max_length=255, unique=True)
    phone = CharField(max_length=255, unique=True, null=True, blank=True)
    birthday = DateField(auto_now_add=True)
    description = TextField(null=True, blank=True)
    majority = CharField(max_length=255, null=True, blank=True)
    photo = ImageField(default='users/desfaultuser.png')
    is_active = BooleanField(default=False)

    objects = UserManager()

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    @property
    def years_old(self):
        return datetime.now().year - self.birthday.year

    @property
    def birthday_date(self):
        return f'{self.birthday.year}-{self.birthday.month}-{self.birthday.day}'


class Category(Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255, unique=True)
    picture = ImageField(upload_to='%m', null=True, blank=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'

    @property
    def blog_count(self):
        return self.blog_set.filter(is_active=Blog.Active.ACTIVE).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            while Category.objects.filter(slug=self.slug).exists():
                slug = Category.objects.filter(slug=self.slug).first().slug
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


class ActiveBlogsManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=Blog.Active.ACTIVE).order_by('created_at')


class CancelBlogsManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=Blog.Active.CANCEL)


class Blog(Model):
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Bloglar'

    class Active(TextChoices):  # A subclass of Enum
        ACTIVE = 'active', _('active')
        CANCEL = 'cancel', _('cancel')
        PENDING = 'pending', _('pending')

    title = CharField(max_length=255, null=True, blank=True)
    author = ForeignKey('apps.CustomUser', SET_NULL, null=True, blank=True)
    description = RichTextUploadingField()
    slug = SlugField(max_length=255, unique=True)
    main_picture = ImageField(upload_to='%m', null=True, blank=True)
    is_active = CharField(max_length=8, choices=Active.choices, default=Active.PENDING)
    category = ManyToManyField(Category)
    created_at = DateTimeField(auto_now_add=True)

    objects = Manager()
    active = ActiveBlogsManager()
    cancel = CancelBlogsManager()

    @register.filter
    def hash(h, key):
        return h[key]

    def status_button(self):
        if self.is_active == Blog.Active.PENDING:
            return format_html(
                f'''<a href="active/{self.id}" class="button">Active</a>
                        <a href="cancel/{self.id}" class="button">Cancel</a>'''
            )
        elif self.is_active == Blog.Active.ACTIVE:
            return format_html(
                f'''<a style="color: green; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlangan</a>''')

        return format_html(
            f'''<a style="color: red; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlanmagan</a>''')

    @property
    def view_count(self):
        n = BlogViewing.view_count(self)
        return n.count()

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


class Comment(Model):
    comment = TextField()
    author = ForeignKey('apps.CustomUser', CASCADE)
    blog = ForeignKey('apps.Blog', CASCADE, related_name='comment_set')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Komentariya'
        verbose_name_plural = 'Komentariyalar'

    def __str__(self):
        return f'{self.author} -> {self.comment[:20]}'


class BlogViewing(Model):
    blog = ForeignKey(Blog, CASCADE)
    viewed_time = DateTimeField(auto_now_add=True)

    def view_count(blog: Blog):
        return BlogViewing.objects.filter(blog=blog)

    def __str__(self):
        return f'{self.blog.id}'


class Message(Model):
    author = ForeignKey(CustomUser, CASCADE)
    subject = CharField(max_length=255)
    message = TextField()
    answer = RichTextUploadingField(null=True, blank=True)
    status = BooleanField(default=False)
    written_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'


class Region(Model):
    name = CharField(max_length=255)


class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('apps.Region', CASCADE)
