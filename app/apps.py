from django.apps import AppConfig


class DbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    # verbose_name = "Приложение"  # Чтобы изменить название при отображении в админ панели (другой вариант приведен в admin.py)
