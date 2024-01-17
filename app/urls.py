from django.urls import path
from .views import IndexView, BlogView, AboutView, PostDetailView, LoginView


app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('blog/<name>/', BlogView.as_view(), name='blog'),
    path('about/', AboutView.as_view(), name='about'),
    path('blog/detail/', PostDetailView.as_view(), name='post-detail'),
    path('login/', LoginView.as_view(), name='login'),
]