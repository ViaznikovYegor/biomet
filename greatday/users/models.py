from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        ADMIN = 'admin', 'Администратор'

    # Дополнительные поля
    height = models.IntegerField(null=True, blank=True, verbose_name='Рост (см)')
    weight = models.IntegerField(null=True, blank=True, verbose_name='Вес (кг)')
    age = models.IntegerField(null=True, blank=True, verbose_name='Возраст')
    is_sick = models.BooleanField(default=False, verbose_name='Болеет')
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
    )

    # Переопределяем связи с группами и правами, указывая уникальный related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='группы',
        blank=True,
        help_text='Группы, к которым принадлежит пользователь.',
        related_name='custom_user_groups',   # уникальное имя обратной связи
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='права пользователя',
        blank=True,
        help_text='Специфические права для этого пользователя.',
        related_name='custom_user_permissions',   # уникальное имя обратной связи
        related_query_name='custom_user',
    )

    class Meta:
        db_table = 'users_user'  # опционально, чтобы таблица называлась users_user
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username