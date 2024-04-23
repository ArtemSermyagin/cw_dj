from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = models.CharField(max_length=150, **NULLABLE)
    surname = models.CharField(max_length=50)
    email = models.EmailField(unique=True, verbose_name='почта')

    class Meta:
        permissions = [
            (
                'manager_site_newsletter',
                'Менеджер'
            )
        ]
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('id',)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Code(models.Model):
    code = models.CharField(max_length=6, verbose_name="Код пользователя")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    def __str__(self):
        return f"{self.code} - {self.user}"


class Client(models.Model):
    '''
    Клиент сервиса:
    контактный email,
    ФИО,
    комментарий.
    '''
    email = models.EmailField(unique=True, verbose_name='почта')
    full_name = models.CharField(max_length=100, verbose_name='ФИО')
    comment = models.TextField(verbose_name='комментарий')
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', **NULLABLE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь (Создатель)")
    is_blocked = models.BooleanField(default=False, verbose_name="Блокировка")

    def __str__(self):
        return f'{self.email}, {self.full_name}, {self.comment}'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        ordering = ('id',)


class Newsletter(models.Model):
    '''
    Рассылка (настройки):
    время рассылки;
    периодичность: раз в день, раз в неделю, раз в месяц;
    статус рассылки: завершена, создана, запущена.
    '''
    PERIOD_DAILY = 'daily'
    PERIOD_WEEKLY = 'weekly'
    PERIOD_MONTHLY = 'monthly'

    PERIODS = (
        (PERIOD_DAILY, 'Ежедневная'),
        (PERIOD_WEEKLY, 'Раз в неделю'),
        (PERIOD_MONTHLY, 'Раз в месяц'),
    )

    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_DONE = 'done'

    STATUSES = (
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_DONE, 'Завершена'),
    )

    time = models.TimeField(verbose_name='время рассылки')
    period = models.CharField(max_length=30, choices=PERIODS, verbose_name='периодичность рассылки')
    status = models.CharField(max_length=30, choices=STATUSES, verbose_name='статус рассылки')
    client = models.ManyToManyField(Client, verbose_name='Клиент')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь (Создатель)")

    def __str__(self):
        return f'{self.time}, {self.period}, {self.status}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        ordering = ('id',)


class Message(models.Model):
    '''
    Сообщение для рассылки:
    тема письма,
    тело письма.
    '''
    theme = models.CharField(max_length=100, verbose_name='тема письма')
    letter = models.TextField(verbose_name='тело письма')
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='messages',
                                   verbose_name='рассылка')

    def __str__(self):
        return f'{self.theme}, {self.letter}'

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'
        ordering = ('id',)


class Log(models.Model):
    '''
    Логи рассылки:
    дата и время последней попытки;
    статус попытки;
    ответ почтового сервера, если он был.
    '''
    date_attempt = models.DateTimeField(verbose_name='дата и время последней попытки')
    state = models.CharField(max_length=50, verbose_name='статус попытки')
    response_server = models.CharField(max_length=250, verbose_name='ответ почтового сервера')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="сообщение")

    def __str__(self):
        return f'{self.date_attempt}, {self.state}, {self.response_server}'

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'
        ordering = ('id',)
