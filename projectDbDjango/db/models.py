from django.db import models
from datetime import date
"""
Рассматриваются 4 таблицы условно обобщающие функционал блога
"""


class Blog(models.Model):
    """
    Таблица Блог, содержащая в себе
    name - название блога
    tagline - используется для хранения краткого описания или слогана блога
    """
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    Таблица Автор, содержащая в себе
    name - username автора
    email - адрес электронной почты автора
    """

    name = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):
        return self.name


class AuthorProfile(models.Model):
    author = models.OneToOneField(Author, on_delete=models.CASCADE)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='avatars/')

    def __str__(self):
        return self.author.name


class Entry(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    body_text = models.TextField()
    pub_date = models.DateField()
    mod_date = models.DateField(default=date.today)
    authors = models.ManyToManyField(Author)
    number_of_comments = models.IntegerField(default=0)
    number_of_pingbacks = models.IntegerField(default=0)
    rating = models.IntegerField(default=5)

    def __str__(self):
        return self.headline
