from django.db import models
from datetime import date, datetime
import hashlib
import os
from django.core.validators import RegexValidator
from PIL import Image
from django.contrib.auth.models import User

"""
Рассматриваются 4 таблицы условно обобщающие функционал блога
"""


class Blog(models.Model):
    """
    Таблица Блог, содержащая в себе
    name - название блога
    tagline - используется для хранения краткого описания или слогана блога
    """
    name = models.CharField(max_length=100,
                            unique=True,
                            verbose_name="Название блога",
                            help_text="Название блога уникальное. Ограничение 100 знаков")

    slug_name = models.SlugField(unique=True,
                                 verbose_name="Slug поле названия",
                                 help_text="Название написанное транслитом, для человекочитаемости. Название уникальное.")

    headline = models.TextField(max_length=255,
                                verbose_name="Короткий слоган",
                                null=True, blank=True,
                                help_text="Ограничение 255 символов.")

    description = models.TextField(null=True, blank=True,
                                   verbose_name="Описание блога",
                                   help_text="О чем этот блог? Для кого он, в чем его ценность?")

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Дата и время создания объекта сущности в базе данных

    updated_at = models.DateTimeField(
        auto_now=True
    )  # Дата и время обновления объекта сущности в базе данных

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блог"
        verbose_name_plural = "Блоги"
        unique_together = (
            'name', 'slug_name'
        )  # Условие на то, что поля 'name' и 'slug_name' должны создавать уникальную группу


def hashed_upload_path(instance, filename):
    """
    Пример замены имени файла на строку <user_hash> для возможного дальнейшего
    использования данных
    """
    # Генерация хэш значения картинки
    file_hash = hashlib.md5(instance.avatar.read()).hexdigest()

    # Получение файлового расширения
    _, ext = os.path.splitext(filename)

    # Новое имя картинки
    new_filename = f"{instance.author.name}_{file_hash}{ext}"

    # Возвращаем полный путь сохранения
    return os.path.join("avatars", new_filename)


class UserProfile(models.Model):
    """
    Дополнительная информация к профилю пользователя, было создано, чтобы показать, как можно
    расширить какую-то модель за счёт использования отношения
    один к одному(OneToOneField).
    user - связь с таблицей user (один к одному(у пользователя может быть только один профиль,
    соответственно профиль принадлежит определенному пользователю))
    bio - текст о себе
    avatar - картинка профиля. Стоят задачи(просто, чтобы показать как это можно решить):
        1. При сохранении необходимо переименовать картинку по шаблону user_hash
        2. Необходимо все передаваемые картинки для аватара приводить к размеру 200х200
    phone_number - номер телефона с валидацией при внесении
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_profile")

    avatar = models.ImageField(upload_to=hashed_upload_path,
                               default='avatars/unnamed.png',
                               null=True,
                               blank=True)

    phone_regex = RegexValidator(
        regex=r'^\+79\d{9}$',
        message="Phone number must be entered in the format: '+79123456789'."
    )
    phone_number = models.CharField(validators=[phone_regex],
                                    max_length=12,
                                    blank=True,
                                    null=True,
                                    unique=True,
                                    help_text="Формат +79123456789",
                                    )  # максимальная длина 12 символов
    city = models.CharField(max_length=120,
                            blank=True,
                            null=True,
                            help_text="Город проживания",
                            )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Дата и время создания объекта сущности в базе данных

    updated_at = models.DateTimeField(
        auto_now=True
    )  # Дата и время обновления объекта сущности в базе данных

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        # Вызов родительского save() метода
        super().save(*args, **kwargs)

        # Открытие картинки
        image = Image.open(self.avatar.path)

        # Определение желаемого размера картинки
        desired_size = (200, 200)

        # Изменение размера
        image.thumbnail(desired_size, Image.ANTIALIAS)

        # Сохранение картинки с перезаписью
        image.save(self.avatar.path)

class AuthorProfile(models.Model):
    """
    Таблица Профиль Автора, содержащая в себе
    name - username автора
    email - адрес электронной почты автора
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="author_profile")

    bio = models.TextField(blank=True,
                           null=True,
                           help_text="Короткая биография",
                           )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Дата и время создания объекта сущности в базе данных

    updated_at = models.DateTimeField(
        auto_now=True
    )  # Дата и время обновления объекта сущности в базе данных

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профиль автора"
        verbose_name_plural = "Профили авторов"



class Entry(models.Model):
    """
    Статья блога
    blog - связь с конкретным блогом (отношением "один ко многим" (one-to-many).
        Одна запись блога (Entry) может быть связана с одним конкретным блогом (Blog),
        но блог (Blog) может иметь множество связанных записей блога (Entry))
    headline - заголовок
    slug_headline - заголовок в транслите
    summary - краткое описание статьи
    body_text - полный текст статьи
    pub_date - дата и время публикации записи
    mod_date - дата редактирования записи
    authors - авторы написавшие данную статью (отношение "многие ко многим"
        (many-to-many). Один автор может сделать несколько записей в блог (Entry),
         и одну запись могут сделать несколько авторов (Author))
    number_of_comments - число комментариев к статье
    number_of_pingbacks -  число отзывов/комментариев на других блогах или сайтах,
        связанных с определенной записью блога (Entry)
    rating - оценка статьи
    """
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="entryes")  # related_name позволяет создать обратную связь
    headline = models.CharField(max_length=255)
    slug_headline = models.SlugField(max_length=255)  # Можно указать primary_key=True, тогда будет идентифицироваться в БД вместо id
    summary = models.TextField()
    body_text = models.TextField()
    pub_date = models.DateTimeField(default=datetime.now)
    mod_date = models.DateField(auto_now=True)
    authors = models.ManyToManyField(AuthorProfile)
    number_of_comments = models.IntegerField(default=0)
    number_of_pingbacks = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    tags = models.ManyToManyField('Tag')

    def __str__(self):
        return self.headline

    class Meta:
        unique_together = ('blog', 'headline', 'slug_headline')
        ordering = ('-pub_date',)  # При выводе запроса проводить сортировку по дате


class Tag(models.Model):
    name = models.CharField(max_length=50,
                            help_text="Ограничение на 50 символов",
                            verbose_name="Имя тега")
    slug_name = models.SlugField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Дата и время создания объекта сущности в базе данных

    updated_at = models.DateTimeField(
        auto_now=True
    )  # Дата и время обновления объекта сущности в базе данных

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             related_name='comments', null=True)
    entry = models.ForeignKey(Entry, on_delete=models.SET_NULL,
                              related_name='comments', null=True)

    text = models.TextField()

    parent = models.ForeignKey('self',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True,
                               related_name='children',
                               verbose_name="родительский комментарий",
                               help_text="Комментарий с которого началась новая ветка",
                               )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Дата и время создания объекта сущности в базе данных

    updated_at = models.DateTimeField(
        auto_now=True
    )  # Дата и время обновления объекта сущности в базе данных

    def __str__(self):
        return f"Пользователь: {self.user.username}; " \
               f"Статья: {self.entry.headline[:30]}; " \
               f"Текст: {self.text[:30]}"

