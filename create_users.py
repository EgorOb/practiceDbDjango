"""Файл для создания пользователей"""

import os
from time import time
import asyncio  # Для асинхронных задач
import threading  # Для создания потоков
from multiprocessing import Pool  # Для создания процессов
from multiprocessing.pool import ThreadPool  # Для создания пула потоков
from concurrent.futures import ThreadPoolExecutor  # Для создания пула потоков
from json import load, dump

from faker import Faker

# _____________Для работы с БД в Django через скрипт - этот блок обязателен !___
from django import setup

# Блок обязательно должен быть определен до импорта моделей БД
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'project.settings')  # Передача параметров в окружение
setup()  # Загрузка настроек Django
# ______________________________________________________________________________

from django.contrib.auth.models import User  # Загрузка базового пользователя

# _____________Блок с созданием пользователей___________________________________

fake = Faker("ru")  # Создаём объект для генерации фейковых данных
Faker.seed(
    42)  # Фиксируем значение seed, чтобы случайные генерации были воспроизводимы

def write_users(data):
    """Запись данных пользователей в файл users.json"""
    if os.path.exists("users.json"):
        with open("users.json", encoding="utf-8") as f:
            users = load(f)
        users += data  # Дозаписываем данные к уже имеющимся
        with open("users.json", "w", encoding="utf-8") as f:
            dump(users, f, indent=4)
    else:
        with open("users.json", "w", encoding="utf-8") as f:
            dump(data, f, indent=4)

def get_fake_user():
    return {
        "username": fake.user_name(),
        "email": fake.free_email(),
        "password": fake.password(),
    }

def create_fake_users(num_users=10, is_staff=False):
    """Создаем несуществующих пользователей и записываем их, чтобы был доступ"""
    t1 = time()
    data = []
    for _ in range(num_users):
        fake_user = get_fake_user()  # Получение данных пользователя
        # Создание объекта в БД
        User.objects.create_user(username=fake_user["username"],
                                 email=fake_user["email"],
                                 password=fake_user["password"],
                                 is_staff=is_staff)
        data.append(fake_user)

    print(f"Время выполнения создания {num_users} пользователей через "
          f"синхронный цикл равно {time() - t1:.4f} c")

    write_users(data)  # Запись в файл


async def async_create_fake_users(num_users=10):
    """
    Асинхронно создаем несуществующих пользователей

    Подробнее про asyncio https://docs.python.org/3/library/asyncio.html
    """
    t1 = time()
    data_user, data = [], []

    for _ in range(num_users):
        fake_user = get_fake_user()  # Получение данных пользователя
        user = User(username=fake_user["username"],
                    email=fake_user["email"])
        # Для передачи пароля используется метод set_password, иначе пароль
        # хранится не в хешированном виде
        user.set_password(fake_user["password"])

        data_user.append(user)
        data.append(fake_user)
    # У объекта БД есть метод save(), а для асинхронного сохранения применяют asave()
    await asyncio.gather(*[user.asave() for user in data_user])
    """
    asyncio.gather - это функция из библиотеки asyncio в Python, которая позволяет вам запускать 
    несколько корутин (асинхронных функций) параллельно и ожидать их завершения.
    В функцию передаются объекты (выполняемые функции), которые необходимо запустить асинхронно
    """

    print(f"Время выполнения создания {num_users} пользователей через "
          f"асинхронный цикл равно {time() - t1:.4f} c")

    write_users(data)  # Запись в файл


def create_user(data_dict):
    user = User(username=data_dict["username"], email=data_dict["email"])
    user.set_password(data_dict["password"])
    user.save()


def create_users_with_threading(num_users=10):
    """
    Обработка запросов через потоки.

    Подробнее про threading https://docs.python.org/3/library/threading.html
    """
    t1 = time()
    data = []
    threads = []  # Объект для хранения потоков, чтобы потом можно было за
    # ними следить в одном месте

    for _ in range(num_users):  # Создание данных и запуск потоков
        fake_user = get_fake_user()  # Получение данных пользователя
        data.append(fake_user)
        t = threading.Thread(target=create_user,
                             args=(fake_user, )
                             )
        t.start()  # Запуск потока
        threads.append(t)

    for t in threads:
        """
        После того как все потоки запущены, второй цикл перебирает их, 
        вызывая метод join() для каждого потока.

        Метод join() блокирует выполнение основного потока (того, который вызвал join) 
        до тех пор, пока поток, для которого он был вызван, не завершится.

        Это гарантирует, что основной поток (который запускает и контролирует все 
        остальные потоки) будет ждать завершения всех дочерних потоков перед 
        продолжением своего выполнения.

        Это важно для обеспечения того, чтобы все пользовательские данные были 
        полностью обработаны и все потоки завершили свою работу, прежде чем программа 
        перейдет к следующим операциям.
        """
        t.join()  # Ожидает завершения каждого потока

    print(f"Время выполнения создания {num_users} пользователей через "
          f"потоки равно {time() - t1:.4f} c")

    write_users(data)  # Запись в файл

def create_users_with_threadpool(num_users=10, num_process=5):
    """
    Более эффективная обработка через пулл потоков при ограничениях на
    число поддерживаемых потоков. Удобно использовать когда есть ограничение на
    количество создаваемых потоков. Потоки не удаляются, а переиспользуются в пуле.
    """
    t1 = time()
    user_data = [get_fake_user() for _ in range(num_users)]  # Создание данных пользователей

    # Использование ThreadPoolExecutor из concurrent.futures для управления потоками
    with ThreadPoolExecutor(max_workers=num_process) as executor:
        results = list(executor.map(create_user, user_data))

    ## Альтернатива - использование ThreadPool из multiprocessing.pool для управления потоками
    # with ThreadPool(processes=num_process) as pool:
    #     results = pool.map(create_user, user_data)

    print(f"Время выполнения создания {num_users} пользователей "
          f"через ThreadPool равно {time() - t1:.4f} с")

    write_users(user_data)  # Запись в файл

def create_users_with_multiprocessing(num_users=10, num_process=5):
    """
    В модуле multiprocessing есть класс Pool, который позволяет управлять пулом
    рабочих процессов и выполнять задачи параллельно в разных процессах.
    Это особенно эффективно для CPU-bound операций, так как позволяет обойти
    ограничения Global Interpreter Lock (GIL) в Python.

    Удобно использовать для задач требующих значительной загрузки ЦП для решения задачи.

    Подробнее про multiprocessing  https://docs.python.org/3/library/multiprocessing.html
    """
    t1 = time()
    user_data = [get_fake_user() for _ in range(num_users)]  # Создание данных пользователей

    with Pool(processes=num_process) as pool:  # Используйте 5 процессов
        results = pool.map(create_user, user_data)

    print(
        f"Время выполнения создания {num_users} пользователей через "
        f"мультипроцессинг равно {time() - t1:.4f} c")
    return results

if __name__ == "__main__":
    # _____________Создание пользователей_______________________________________
    # Создание администратора
    User.objects.create_superuser("admin", password="123")
    print("Админ создан \n    Логин: admin\n    Пароль: 123")

    create_fake_users(2, True)  # Создание аккаунта для персонала

    create_fake_users(5)  # Работает долго, хеширование пароля занимает много времени

    # Используем asyncio.run() для запуска асинхронной функции
    asyncio.run(async_create_fake_users(5))  # Работает аналогично по времени как
    # create_fake_users, так как для ускорения хеширования нужно параллелить
    # процессы

    create_users_with_threading(10)  # Применение потоков позволило ускорить
    # обработку хеширования паролей

    create_users_with_threadpool(10)  # А пулл потоков для этой задачи справился похуже

    create_users_with_multiprocessing(10)  # Применение мультипроцессинга,
    # дало результат хуже, чем с потоками

