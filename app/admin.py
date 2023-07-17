from django.contrib import admin
from .models import Blog, Entry, Author, AuthorProfile

admin.site.register(Blog)
admin.site.register(Entry)
admin.site.register(Author)
admin.site.register(AuthorProfile)
