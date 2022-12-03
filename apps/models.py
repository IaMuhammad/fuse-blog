from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, SlugField, CharField, ForeignKey, CASCADE, DateField, TextField, ImageField, \
    SET_NULL, ManyToManyField, SET_DEFAULT, EmailField, TextChoices
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = EmailField(max_length=255, unique=True)
    phone = CharField(max_length=255, unique=True)
    birthday = DateField(auto_now=True)
    description = TextField(null=True, blank=True)
    majority = CharField(max_length=255, null=True, blank=True)
    photo = ImageField(default='users/defaauluser.png')


class Category(Model):
    name = CharField(max_length=255)
    picture = ImageField(upload_to='%m', null=True, blank=True)
    slug = SlugField(max_length=255, unique=True)

    @property
    def blog_count(self):
        return self.blog_set.count()

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
            return format_html(f'''<a style="color: green; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlangan</a>''')

        return format_html(f'''<a style="color: red; font-size: 1em;margin-top: 8px; margin: auto;">Tasdiqlanmagan</a>''')

    """
    category, 
    image
    """

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
    created_at = DateField(auto_now=True)

    def __str__(self):
        return f'{self.author} -> {self.coment[:20]}'
