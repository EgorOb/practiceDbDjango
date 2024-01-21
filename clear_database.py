"""
Удаление базы данных. Создание структуры БД, создание миграций
"""

import os
import subprocess
from project.settings import  DATABASES


DATABASE = DATABASES["default"]["NAME"]
command_make = "python manage.py makemigrations"
command_migrate = "python manage.py migrate"


if os.path.exists(DATABASE):
    os.remove(DATABASE)

if os.path.exists("users.json"):
    os.remove("users.json")

try:
    subprocess.run(command_make, shell=True, check=True)
    subprocess.run(command_migrate, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Ошибка выполнения команды: {e}")

