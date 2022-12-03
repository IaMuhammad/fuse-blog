from django.urls import path

from apps.views import MainPageView, BlogListView, AboutPageView, ContactPageVIew, BlogPageView, RegisterPageView, \
    LoginPageView, CustomLogoutView, UserUpdateView, VerifyView, CreateCommentBLog

urlpatterns = [
    path('', MainPageView.as_view(), name='main_view'),
    path('blog-category/<str:slug>', BlogListView.as_view(), name='blog_category_view'),
    path('about', AboutPageView.as_view(), name='about_view'),
    path('contact', ContactPageVIew.as_view(), name='contact_view'),
    path('blog/<str:slug>', BlogPageView.as_view(), name='post_view'),
    path('blog/<str:slug>/create', CreateCommentBLog.as_view(), name='comment_view'),

    path('user-edit/<int:pk>', UserUpdateView.as_view(), name='user_update_view'),
    path('register', RegisterPageView.as_view(), name='register_view'),
    path('login', LoginPageView.as_view(), name='login_view'),
    path('logout', CustomLogoutView.as_view(), name='logout_view'),
    path('verify', VerifyView.as_view(), name='verify_view'),
]
