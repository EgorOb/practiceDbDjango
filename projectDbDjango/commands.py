import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectDbDjango.settings')
django.setup()

if __name__ == "__main__":
    from db.models import Blog, Author, AuthorProfile, Entry
    """Проверьте тут код если необходимо"""
    from django.db.models import Count
    blogs = Blog.objects.alias(entries=Count('entry')).filter(entries__gt=4)
    print(blogs)
    """
    <QuerySet [
    <Blog: Путешествия по миру>, 
    <Blog: Кулинарные искушения>, 
    <Blog: Фитнес и здоровый образ жизни>, 
    <Blog: ИТ-новости и технологии>, 
    <Blog: Мода и стиль>
    ]>
    """
    ## Выведет ошибку, так как поле entries не существует, виду различий между alias и annotate
    # blogs = Blog.objects.alias(entries=Count('entry')).filter(entries__gt=4).values('blog', 'entries')












