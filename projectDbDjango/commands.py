import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectDbDjango.settings')
django.setup()

if __name__ == "__main__":
    from db.models import Blog, Author, AuthorProfile, Entry
    """Проверьте тут код если необходимо"""













