"""
Заполнение данных в БД через скрипт python.
Для заполнения, достаточно просто запустить скрипт.

Так же приведенные команды в блоке (if __name__ == "__main__":)
можно аналогично выполнить в окружении запускаемом командой
python manage.py shell

В случае вызова консоли (python manage.py shell), то так же как и в
приведенном блоке (if __name__ == "__main__":) необходимо
импортировать модели с которыми будете работать и далее выполнять команды с БД.
"""

import django
import os
from json import load
from django.core.exceptions import ValidationError
from django.core.files import File
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectDbDjango.settings')
django.setup()

with open("blogs.json", encoding="utf-8") as f:
    data_blog = load(f)
with open("authors.json", encoding="utf-8") as f:
    data_author = load(f)
with open("authors_profile.json", encoding="utf-8") as f:
    data_author_profile = load(f)
with open("entrys.json", encoding="utf-8") as f:
    data_entry = load(f)

if __name__ == "__main__":
    from db.models import Blog, Author, AuthorProfile, Entry

    # ______Работа с объектами таблицы Blog__________
    """Пример записи в БД с последующим сохранением"""
    obj = Blog(name=data_blog[0]["name"], tagline=data_blog[0]["tagline"])
    obj.save()

    """Пример записи в БД с сохранением (в нашем случае, так как работаем с словарём,
    то можно применить распаковку **)"""
    Blog.objects.create(**data_blog[1])

    """Никто не запрещает использовать циклы, минус в том, что при работе с циклами
    каждая запись сохраняется в БД по одному, что может создавать дополнительную
    нагрузку на БД"""
    for data in data_blog[2:]:
        Blog.objects.create(**data)

    # ______Работа с объектами таблицы Author__________
    """Если необходимо записать объекты пакетом, то для этих целей существует bulk_create,
    Однако он записывает данные в БД, если это контейнер подготовленных объектов
    к записи, а не сырые данные."""
    data_for_write = [Author(**data) for data in data_author[:10]] # Здесь
    # просто создались объекты, записи в БД не было
    Author.objects.bulk_create(data_for_write) # А здесь произошла пакетная запись в БД

    """
    При использовании Django ORM в Python - скрипте или через оболочку shell,
    встроенные проверки полей моделей автоматически не выполняются при сохранении
    объектов в базу данных. Однако возможно явно вызвать эти проверки и обработать
    возможные исключения, чтобы убедиться, что данные соответствуют заданным
    ограничениям полей для этого у объекта, который создали для записи необходимо
    вызвать метод full_clean()

    Для более наглядной части создам функцию с проверкой
    """
    def check_obj_for_write_to_db(obj, save=True):
        try:
            obj.full_clean()
        except ValidationError as e:
            fields = obj._meta.fields  # Получение
            # всех полей у объекта, необходимо чтобы вывести в трассировке
            # с какими параметрами был объект с ошибками. Выводит без полей с
            # отношениями с другими таблицами
            params = ""
            for field in fields:
                field_name = field.name
                field_value = getattr(obj, field_name)
                params += f"{field_name}={field_value!r}, "
            print(f"Ошибка при создании объекта: {e}\n"
                  f"Объект: {obj.__class__.__name__}({params[:-2]})")
        else:
            if save:
                obj.save()  # Объект успешно создан
            return True
        return False

    """Пример одиночной записи с проверкой, в случае удачных проверок - запишется,
    если нет, то появится ошибка, но выполнению кода это не помешает, так как
    был специально написан обработчик исключения в check_obj_for_write_to_db"""
    obj = Author(**data_author[10])
    check_obj_for_write_to_db(obj)

    """Пример с ошибкой"""
    obj = Author(name="user", email="user")
    check_obj_for_write_to_db(obj)
    """
    В консоль выведется
    Ошибка при создании объекта: {'email': ['Enter a valid email address.']}
    Объект: Author(id=None, name='user', email='user')"""

    """
    К сожалению для Author.objects.create(**data_author[10]) не получится провести
    встроенные проверки, так как внутри вызывается save() который делает базовые проверки.

    Для bulk_create аналогичная ситуация, однако можно провести проверки в момент
    формирования контейнера объектов для записи. Ниже приведён пример как можно
    это сделать. В рассматриваемом примере если существует хотя бы одна ошибка,
    то весь блок не записывается.
    """

    """Пример с ошибкой в блоке"""
    raw_data = [{"name": "user1", "email": "user1"}] + data_author[11:]
    data_for_write = list(filter(lambda x: check_obj_for_write_to_db(x, False),
                                 (Author(**data) for data in raw_data)))
    if len(data_for_write) == len(raw_data):
        Author.objects.bulk_create(data_for_write)
    """
    В консоль выведется
    Ошибка при создании объекта: {'email': ['Enter a valid email address.']}
    Объект: Author(id=None, name='user1', email='user1')"""

    """Рабочий пример"""
    raw_data = data_author[11:]
    data_for_write = list(
        filter(lambda x: check_obj_for_write_to_db(x, False),
               (Author(**data) for data in raw_data)))
    if len(data_for_write) == len(raw_data):
        Author.objects.bulk_create(data_for_write)

    # ______ Работа с объектами таблицы AuthorProfile __________
    """Далее рассмотрим создание объектов с отношениями. Для того чтобы создать
    запись в БД в таблице где есть отношение, то в это поле необходимо передавать
    объект базы данных связанный с необходимым ключом(значением).

    """
    for data in data_author_profile:
        author = Author.objects.get(name=data["author"])
        if data["avatar"] is not None:  # Из-за того, что avatar имеет значение
            # по умолчанию, то None не считается пустым для обработчика, поэтому
            # приходится разделять на 2 случая, с и без параметрами avatar. Значение
            # по умолчанию подставляется когда параметр не передан, а NULL подставляется
            # (если в модели определили null=True) если был передан None
            obj = AuthorProfile(author=author,
                                bio=data["bio"],
                                avatar=data["avatar"],
                                phone_number=data["phone_number"],
                                city=data["city"])
        else:
            obj = AuthorProfile(author=author,
                                bio=data["bio"],
                                phone_number=data["phone_number"],
                                city=data["city"])

        check = check_obj_for_write_to_db(obj)

        """чтобы провести теже действия, что проводит Django при сохранении файла
        необходимо вызвать save от этого поля, это немного отличается от ранее
        рассмотренной валидации, так как тут рассматривается конкретное поле со своей спецификой
        """
        if check and data["avatar"] is not None:  # Если ошибок нет, то запускаем протокол сохранения картинки
            with open(data["avatar"], 'rb') as file:
                image_file = File(file)
                obj.avatar.save(os.path.basename(data["avatar"]), image_file)

    ## ______ Работа с объектами таблицы Entry __________
    blogs = Blog.objects.all()
    authors = Author.objects.all()
    for entry in data_entry:
        blog = blogs.get(name=entry["blog"])
        author = authors.filter(name__in=entry["authors"])
        pub_date = date(*map(int, entry["pub_date"].split("-"))) if \
            entry["pub_date"] is not None else date.today()
        obj = Entry(blog=blog,
                    headline=entry["headline"],
                    body_text=entry["body_text"],
                    pub_date=pub_date,
                    number_of_comments=entry["number_of_comments"],
                    number_of_pingbacks=entry["number_of_pingbacks"],
                    rating=entry["rating"] if entry["rating"] is not None else 0.0)

        check_obj_for_write_to_db(obj)
        obj.authors.set(author) # Запись отнощение многое ко многому немного специфичная
        # необходимо сначала сохранить в БД, а затем установить значения отношений
