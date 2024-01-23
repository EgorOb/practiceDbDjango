from django.contrib import admin
from .models import Blog, Entry, UserProfile, AuthorProfile, Tag, Comment
from django.apps import apps

app = apps.get_app_config('app')
app.verbose_name = 'Приложение'  # Чтобы изменить название при отображении в админ панели (другой вариант приведен в apps.py)

admin.site.register(Blog)
admin.site.register(Entry)
admin.site.register(UserProfile)
admin.site.register(AuthorProfile)
admin.site.register(Tag)
admin.site.register(Comment)
