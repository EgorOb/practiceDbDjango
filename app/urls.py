from django.urls import path
from .views import IndexView, BlogView, AboutView, PostDetailView


app_name = 'app'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('about/', AboutView.as_view(), name='about'),
    path('blog/detail/', PostDetailView.as_view(), name='post-detail'),
]