from django.urls import path

from apps import views
from apps.views import MainPageView, BlogListView, AboutPageView, ContactPageVIew, BlogPageView, RegisterPageView, \
    LoginPageView, CustomLogoutView, UserUpdateView, VerifyView, \
    AddBlogPageView, ForgotPasswordView, GeneratePdf, ActivateEmailView, ChangePasswordView, ResetPasswordView

urlpatterns = [
    # path('celery', test, name='test'),
    # path('send_mail/', send_mail_to_all, name='sendmail'),

    path('', MainPageView.as_view(), name='main_view'),
    path('blog-category/<str:slug>', BlogListView.as_view(), name='blog_category_view'),
    path('about', AboutPageView.as_view(), name='about_view'),
    # path('contact', ContactPageVIew.as_view(), name='contact_view'),
    path('contact/<str:username>', ContactPageVIew.as_view(), name='contact_view'),
    path('add_blog', AddBlogPageView.as_view(), name='add_blog_view'),
    path('blog/<str:slug>', BlogPageView.as_view(), name='post_view'),
    path('pdf/<str:slug>', GeneratePdf.as_view(), name='make_pdf'),

    path('user-edit/<str:username>', UserUpdateView.as_view(), name='user_update_view'),
    path('register', RegisterPageView.as_view(), name='register_view'),
    path('login', LoginPageView.as_view(), name='login_view'),
    path('logout', CustomLogoutView.as_view(), name='logout_view'),
    path('activate/<str:uid>/<str:token>', ActivateEmailView.as_view(), name='confirm_mail'),
    path('forget', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset/<str:uid>/<str:token>', ResetPasswordView.as_view(), name='reset'),
    path('change_password', ChangePasswordView.as_view(), name='change_password'),
]
