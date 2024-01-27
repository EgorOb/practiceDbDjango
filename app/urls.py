from django.urls import path
from .views import IndexView, BlogView, AboutView, PostDetailView, \
    PersonalAccountView, LoginView, AboutServiceView, LogoutView


app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('blog/<slug:name>/', BlogView.as_view(), name='blog'),
    path('about/', AboutView.as_view(), name='about'),
    path('about/service/', AboutServiceView.as_view(), name='about-service'),
    path('blog/post/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('personal/', PersonalAccountView.as_view(), name='personal-account'),
    path('login/<param>/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

