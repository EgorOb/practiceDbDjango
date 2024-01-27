import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

if __name__ == "__main__":
    from app.models import Blog, UserProfile, AuthorProfile, Entry, Tag, Comment













