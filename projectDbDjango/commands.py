import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectDbDjango.settings')
django.setup()

if __name__ == "__main__":
    from db.models import Blog, Author, AuthorProfile, Entry
    """Проверьте тут код если необходимо"""

    filtered_data = Blog.objects.filter(id__gte=2)
    print(filtered_data)  # прямой порядок
    filtered_data.reverse()
    print(filtered_data)  # обратный порядок
    print(filtered_data.reverse())  # прямой порядок









