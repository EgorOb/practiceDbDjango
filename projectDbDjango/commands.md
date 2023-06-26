# Описание возможностей, по составлению запросов

## Применяемые методы
### all()
Вывод всех значений в таблице ```objects.all()```
```python
all_obj = Blog.objects.all()
print("Вывод всех значений в таблице Blog\n", all_obj)
```
### first()
Вывод первого значения ```objects.first()```
```python
all_obj = Blog.objects.first()
print("Вывод первого значения в таблице Blog\n", all_obj)
```
### Последовательность запросов
Также можно вывести так, так как QuerySet не выполяются сразу и можно делать разные запросы
последовательно сужая область, при этом запросы останутся. QuerySet выполнится при обращении к нему: list, for, print,
получение объекта по индексу и т.д.
```python
all_obj = Blog.objects.all()
obj_first = all_obj.first()
print("Разные запросы на вывод в Blog\n", f"Первое значение таблицы = {obj_first}\n",
       f"Все значения = {all_obj}")
```
### Итерируемость
Объект QuerySet итерируемый, а значит есть возможность обращения через [] и слайсирование, for и т.д
```python
all_obj = Blog.objects.all()
for idx, value in enumerate(all_obj):
    print(f"idx = {idx}, value = {value}")
print(all_obj[0])  # Получение 0-го элемента
print(all_obj[2:4])  # Получение 2 и 3 элемента
"""Получение последнего элемента не осуществимо через обратный индекс
all_obj[-1] - нельзя
можно воспользоваться latest('<name_field>'), где <name_field> - имя колонки в БД.

Почти все операции над БД не требуют предварительного получения всех элементов, постоянная запись Blog.objects.all()
просто для примера.
"""
print(all_obj.latest("id"))  # Получение последнего элемента
print(Blog.objects.latest("id"))  # Одинаково работает
```
### get()
Для получения конкретного элемента необходимо использовать ```objects.get(**conditions)```, где ```**conditions``` - условия
их может быть не одно. get - возвращает только одно значение, если при ваших условиях возвращается не одно значение,
значит необходимо использовать что-то другое, допустим ```objects.filter(**conditions)```. В условиях вы передаёте что необходимо
вывести строки БД при таких значениях полей
```python
# Пример получения элемента по одному условию
print(Blog.objects.get(id=1))
# Пример получения элемента по двум условиям. Условия работают с оператором И, т.е. выведется строка, только с
# совпадением и первого и второго параметра.
print(Blog.objects.get(id=1, name="Путешествия по миру"))
# Если нет совпадений, то выйдет исключение "db.models.Blog.DoesNotExist: Blog matching query does not exist."
print(Blog.objects.get(id=2, name="Путешествия по миру"))
```

### filter()
Когда необходимо вывести более одного значения то можно использовать objects.filter(**conditions), **conditions
аналогично get(**conditions)
```python
print(Blog.objects.filter(id__gte=2))  # Вывод всех строк таблицы Blog у которых значение id >= 2. 
# Рассмотрение поиска по полям далее
```

### exclude()
Аналогично фильтру, только противоположность. Возвращает новый QuerySet, содержащий объекты, которые не соответствуют 
указанным параметрам поиска.
```python
print(Blog.objects.exclude(id__gte=2))  # Вывод всех строк таблицы Blog у которых значение id >= 2. 
# Рассмотрение поиска по полям далее
```

### exists()
Для проверки существования элемента(ов) в БД есть exists(), правда он применяется прямо к объекту, но только 
к объекту ```objects.filter(**conditions).exists()```

Для get придётся использовать блок try-except и ловить исключение ```MyModel.DoesNotExist```, где MyModel ваша модель
```python
# Пример для get
try:
    Blog.objects.get(id=2, name="Путешествия по миру")
except Blog.DoesNotExist:
    print("Не существует")
# Пример для filter
print(Blog.objects.filter(id=2, name="Путешествия по миру").exists())
```

### count()
Чтобы подсчитать количество записей в запросе существует метод count() который применяют к объекту запроса
```python
print(Blog.objects.count())  # Можно ко всей таблице
print(Blog.objects.filter(id__gte=2).count())  # Можно к запросу
all_data = Blog.objects.all()
filtred_data = all_data.filter(id__gte=2)
print(filtred_data.count())  # Можно к частным запросам
```
### order_by()
По умолчанию результаты, возвращаемые QuerySet, упорядочиваются с помощью кортежа, заданного параметром ordering в классе 
Meta модели. Вы можете переопределить это для каждого QuerySet, используя метод ```order_by```

```python
filtered_data = Blog.objects.filter(id__gte=2)
print(filtered_data.order_by("id"))  # упорядочивание по возрастанию по полю id
print(filtered_data.order_by("-id"))  # упорядочивание по уменьшению по полю id
print(filtered_data.order_by("-name", "id"))  # упорядочивание по двум параметрам, сначала по первому на уменьшение,
# затем второе на увеличение. Можно упорядочивание провести по сколь угодно параметрам.
```
### reverse()
Изменение порядка вывода элемента из QuerySet. Если вам нужно просто изменить порядок элементов в наборе запросов 
на обратный без сортировки по конкретному полю, вы можете использовать метод ```reverse()```
```python
filtered_data = Blog.objects.filter(id__gte=2)
print(filtered_data.order_by("id"))  # упорядочивание по возрастанию по полю id
print(filtered_data.order_by("-id"))  # упорядочивание по уменьшению по полю id
print(filtered_data.order_by("-name", "id"))  # упорядочивание по двум параметрам, сначала по первому на уменьшение,
# затем второе на увеличение. Можно упорядочивание провести по сколь угодно параметрам.
```
### distinct()
Возвращает новый QuerySet, который использует SELECT DISTINCT в своем SQL-запросе. 
Это исключает повторяющиеся строки из результатов запроса.
```python
Entry.objects.order_by('author', 'pub_date').distinct('author', 'pub_date')
```
### values()
Возвращает QuerySet, который возвращает словари, а не экземпляры модели, когда используется как итеративный.

Каждый из этих словарей представляет объект с ключами, соответствующими именам атрибутов объектов модели.

В этом примере сравниваются словари values() с объектами нормальной модели:
```python
# This list contains a Blog object.
>>> Blog.objects.filter(name__startswith='Beatles')
<QuerySet [<Blog: Beatles Blog>]>

# This list contains a dictionary.
>>> Blog.objects.filter(name__startswith='Beatles').values()
<QuerySet [{'id': 1, 'name': 'Beatles Blog', 'tagline': 'All the latest Beatles news.'}]>

>>> Blog.objects.values()
<QuerySet [{'id': 1, 'name': 'Beatles Blog', 'tagline': 'All the latest Beatles news.'}]>
>>> Blog.objects.values('id', 'name')
<QuerySet [{'id': 1, 'name': 'Beatles Blog'}]>
```

### values_list()
Это похоже на values(), за исключением того, что вместо возврата словарей он 
возвращает кортежи при повторении. Каждый кортеж содержит значение из 
соответствующего поля или выражения, переданное в вызов values_list() - поэтому 
первый элемент является первым полем и т.д. Например:
```python
>>> Entry.objects.values_list('id', 'headline')
<QuerySet [(1, 'First entry'), ...]>
>>> from django.db.models.functions import Lower
>>> Entry.objects.values_list('id', Lower('headline'))
<QuerySet [(1, 'first entry'), ...]>
```
### union(), intersection(), difference()
Использует оператор SQL UNION для объединения результатов двух или более QuerySet’ов
```python
qs1.union(qs2, qs3)
```
Использует оператор SQL INTERSECT для возврата общих элементов двух или более QuerySet’ов. Например:
```python
qs1.intersection(qs2, qs3)
```
Использует оператор SQL EXCEPT для хранения только элементов, присутствующих в QuerySet, 
но не в каких-либо других QuerySet’ах. Например:
```python
qs1.difference(qs2, qs3)
```
### select_related()
Возвращает QuerySet, который будет «следовать» отношениям внешнего ключа, выбирая 
дополнительные данные связанного объекта при выполнении своего запроса. Это повышение 
производительности, которое приводит к одному более сложному запросу, но означает, 
что дальнейшее использование отношений внешнего ключа не потребует запросов к базе данных.

Следующие примеры иллюстрируют разницу между простыми поисками и с использованием select_related(). 
Вот стандартный поиск:
```python
# Hits the database.
e = Entry.objects.get(id=5)

# Hits the database again to get the related Blog object.
b = e.blog
```
```python
# Hits the database.
e = Entry.objects.select_related('blog').get(id=5)

# Doesn't hit the database, because e.blog has been prepopulated
# in the previous query.
b = e.blog
```
Вы можете ссылаться на любое отношение ForeignKey или OneToOneField в списке полей, 
передаваемых в select_related().

### prefetch_related()
Возвращает ```QuerySet```, который автоматически извлекает в одном пакете связанные 
объекты для каждого из указанных поисков.

```prefetch_related``` имеет цель, аналогичную ```select_related```, в том смысле, что оба предназначены 
для урезания количества запросов к базе данных, вызванного доступом к связанным объектам, 
но стратегия совершенно иная.

```select_related``` работает путем создания соединения (join) SQL и включения полей 
связанного объекта в оператор SELECT. По этой причине ```select_related``` 
получает связанные объекты в одном запросе к базе данных. Тем не менее, чтобы 
избежать гораздо большего результирующего набора, который мог бы возникнуть в 
результате объединения через отношение „many“, ```select_related``` ограничен 
однозначными отношениями - внешним ключом и один-к-одному.

Например, предположим, у вас есть эти модели:

```python
from django.db import models

class Topping(models.Model):
    name = models.CharField(max_length=30)

class Pizza(models.Model):
    name = models.CharField(max_length=50)
    toppings = models.ManyToManyField(Topping)

    def __str__(self):
        return "%s (%s)" % (
            self.name,
            ", ".join(topping.name for topping in self.toppings.all()),
        )
    
>>> Pizza.objects.all()
["Hawaiian (ham, pineapple)", "Seafood (prawns, smoked salmon)"...
```
Проблема в том, что каждый раз, когда Pizza.str() запрашивает self.toppings.all(), он должен запросить базу данных, поэтому Pizza.objects.all() выполнит запрос к таблице Toppings для каждого элемента в Pizza QuerySet.

Мы можем сократить до двух запросов, используя ```prefetch_related```:
```python
Pizza.objects.prefetch_related('toppings')
```

## Поиск по полю

Поиск по полю - это то, как вы определяете содержание предложения SQL WHERE.

Поиск по полю происходит после знака ```__``` . Сначала пишите поле, затем применяете к нему метод через ```__```

При помощи ```__``` вы можете ```получать доступ к связанным полям``` и дальше уже работать с тем полем

Например необходимо вывести все записи блогов, где у автора в имени содержится 'writer'.

```python
obj = Entry.objects.filter(authors__name__contains='writer')
print(obj)
"""<QuerySet [<Entry: Оазисы Сахары: красота и опасность>, 
<Entry: Экзотические специи и их использование>, 
<Entry: Гастрономическое путешествие по Франции>, 
<Entry: Секреты успешного похудения>]>"""
```
Заметьте, как идёт подключение. Мы пытаемся из таблицы Entry через ```filter``` 
обратиться к полю ```authors``` (которое является связанное отношением многое-ко-многому 
(абсолютно так же делается с отношением
один-к-многому)), у ```authors``` содержатся ссылки на таблицу ```Author``` у
которой есть поле ```name```, поэтому мы подключаемся к ней через ```__``` (именно из-за этих соображений
не разрешено называть поле при формировании модели как ```__``` или название поля оканчиваться на ```_```) 

Но, через ```__``` можно и подключится к объектам, у которых нет прямой связи, но есть косвенная.
Допустим модель ```Author``` и ```AuthorProfile```. У ```AuthorProfile``` есть связь ```OneToOneField``` с
```Author```, но обратной связи мы не прописываем, а она есть. Можно идти как вперед,
так и назад.

Поэтому можно решить такую задачу, как вывод всех записей блогов, 
где у автора не указан город.

```python
obj = Entry.objects.filter(authors__authorprofile__city=None)
print(obj)
"""<QuerySet [<Entry: Знакомство с Парижем>, <Entry: Оазисы Сахары: красота и опасность>, 
<Entry: Экзотические специи и их использование>, <Entry: Гастрономическое путешествие по Франции>, 
<Entry: Инновации в области виртуальной реальности>, <Entry: Тенденции моды на текущий сезон>]>"""
```
Однако для такого случая необходимо указывать таблицу где есть данное поле. 
В поле ```authors```
идёт ссылка на таблицу ```Author```, у которой нет явного поля ```city```, но есть
неявная связь с таблицей ```AuthorProfile``` по первичному ключу, поэтому мы этим пользуемся
и указываем связь ```authors__authorprofile```, ну а далее раз связь настроена, 
то подключаемся к полю ```city``` таблицы ```AuthorProfile```.

### exact, iexact
Точное совпадение c учетом и без учёта (работает не во всех БД) регистра соответственно.
```python
print(Entry.objects.get(id__exact=4))
print(Entry.objects.get(id=4))  # Аналогично exact
print(Blog.objects.get(name__iexact="Путешествия по миру"))
```
### contains, icontains
Чувствительный, нечувствительное к регистру поиск
```python
Entry.objects.get(headline__contains='Lennon')
Entry.objects.get(headline__icontains='Lennon')

```
### in
Проверка вхождения
```python
Entry.objects.filter(id__in=[1, 3, 4])
Entry.objects.filter(headline__in='abc')
```
Вы также можете использовать набор запросов для динамической оценки списка значений 
вместо предоставления списка литеральных значений:
```python
inner_qs = Blog.objects.filter(name__contains='Cheddar')
entries = Entry.objects.filter(blog__in=inner_qs)
```
### gt, gte, lt, lte
Больше чем; Больше равно чем; Меньше чем; Меньше равно чем
```python
Entry.objects.filter(id__gt=4)
```
### startswith, istartswith, endswith, iendswith
Начинается с (с/без учетом регистра), заканчивается на (с/без учетом регистра).
```python
Entry.objects.filter(headline__startswith='Lennon')
Entry.objects.filter(headline__istartswith='Lennon')
Entry.objects.filter(headline__endswith='Lennon')
Entry.objects.filter(headline__iendswith='Lennon')
```
### range
Диапазон проверки (включительно).
```python
import datetime
start_date = datetime.date(2005, 1, 1)
end_date = datetime.date(2005, 3, 31)
Entry.objects.filter(pub_date__range=(start_date, end_date))
```
### year, month, day, week, week_day, quarter, hour, minute, second
Для полей даты и даты и времени точное совпадение года, месяца, дня, недели, 
дня недели, квартала, часа, минуты, секунды.
```python
Entry.objects.filter(pub_date__year=2005)
Entry.objects.filter(pub_date__year__gte=2005)
...
```
### date, time
Для полей даты и времени преобразует значение как дату или время.
```python
Entry.objects.filter(pub_date__date=datetime.date(2005, 1, 1))
Entry.objects.filter(pub_date__date__gt=datetime.date(2005, 1, 1))

Entry.objects.filter(pub_date__time=datetime.time(14, 30))
Entry.objects.filter(pub_date__time__range=(datetime.time(8), datetime.time(17)))
```
### isnull
Принимает True или False, которые соответствуют SQL-запросам IS NULL и IS NOT NULL, соответственно
```python
Entry.objects.filter(pub_date__isnull=True)
```
### regex, iregex
Чувствительное/нечувствительное к регистру совпадение регулярного выражения.
```python
Entry.objects.get(title__regex=r'^(An?|The) +')
Entry.objects.get(title__iregex=r'^(an?|the) +')
```



## Q объекты

## ExpressionWrapper()

## Case

## When

## With

## Subquery()

## Необработанные выражения SQL

## Функции окна