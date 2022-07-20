from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
# Функция перевода текса
from django.utils.translation import gettext_lazy as _

from django_rest_passwordreset.tokens import get_token_generator

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class UsersManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError(_('The given email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Users(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer', verbose_name='Тип пользователя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    patronymic = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    company = models.CharField(max_length=50, blank=True, verbose_name='Компания')
    position = models.CharField(max_length=50, blank=True, verbose_name='Должность')
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(_('nickname'), max_length=150, null=True, blank=True,
                                help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                validators=[username_validator],
                                error_messages={'unique': _("A user with that username already exists.")}
                                )

    is_active = models.BooleanField(_('active'), default=False,
                                    help_text=_('Designates whether this user should be treated as active. '
                                                'Unselect this instead of deleting accounts.'),)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UsersManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'


class Contacts(models.Model):
    user_id = models.ForeignKey(Users, verbose_name='Пользователь',
                                related_name='contacts', on_delete=models.CASCADE)

    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    build = models.CharField(max_length=100, verbose_name='Дом')
    corpus = models.CharField(max_length=100, blank=True, verbose_name='Корпус')
    apartment = models.CharField(max_length=100, blank=True, verbose_name='Квартира')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')

    class Meta:
        db_table = 'contacts'
        verbose_name = 'Контактные данные'
        verbose_name_plural = 'Контактные данные'


class Shops(models.Model):
    user_id = models.OneToOneField(Users,
                                   verbose_name='Пользователь', blank=True, null=True,
                                   on_delete=models.CASCADE)

    name = models.CharField(max_length=50, verbose_name='Название магазина')
    url_shop = models.URLField(verbose_name='Ссылка', max_length=50, blank=True)
    status_work = models.BooleanField(default=True, verbose_name='Статус приёма заказов')

    class Meta:
        db_table = 'shops'
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('-name',)


class Categories(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Категория')
    shops = models.ManyToManyField(Shops, related_name='categories', verbose_name='Магазины')

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-name',)


class Products(models.Model):
    category_id = models.ForeignKey(Categories,
                                    verbose_name='Категория',
                                    related_name='products',
                                    on_delete=models.CASCADE)

    name = models.CharField(max_length=150, verbose_name='Название товара')

    class Meta:
        db_table = 'products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)


class ProductsInfo(models.Model):
    shop_id = models.ForeignKey(Shops, verbose_name='Магазины', on_delete=models.CASCADE)
    product_id = models.ForeignKey(Products, verbose_name='Товар', on_delete=models.CASCADE)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД', null=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        db_table = 'products_info'
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product_id', 'shop_id', 'external_id'], name='unique_product_info'),
        ]


class Parameters(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название параметра')

    class Meta:
        db_table = 'parameters'
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Имена параметров'
        ordering = ('-name',)


class ProductParameter(models.Model):
    product_info_id = models.ForeignKey(ProductsInfo, verbose_name='Информация о продукте',
                                        related_name='product_parameters', on_delete=models.CASCADE)

    parameter_id = models.ForeignKey(Parameters, verbose_name='Параметр', null=True,
                                     related_name='product_parameters', on_delete=models.CASCADE)

    value = models.CharField(max_length=100, verbose_name='Значение параметра')

    class Meta:
        db_table = 'product_parameter'
        verbose_name = 'Параметр продукта'
        verbose_name_plural = "Список параметров продукта"
        constraints = [
            models.UniqueConstraint(fields=['product_info_id', 'parameter_id'], name='unique_product_parameter'),
        ]


class Orders(models.Model):
    user_id = models.ForeignKey(Users,
                                verbose_name='Пользователь',
                                related_name='orders',
                                on_delete=models.CASCADE)

    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATE_CHOICES, max_length=20, verbose_name='Статус')
    contact = models.ForeignKey(Contacts, verbose_name='Контакт', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Заказы"
        ordering = ('-date',)


class OrderItems(models.Model):
    order_id = models.ForeignKey(Orders, verbose_name='Заказ', related_name='ordered_items', on_delete=models.CASCADE)
    product_info_id = models.ForeignKey(ProductsInfo, verbose_name='Информация о продукте',
                                        related_name='ordered_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = "Список заказанных товаров"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info_id'], name='unique_order_item'),
        ]


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        Users,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь, который связан с этим токеном подтверждения почты")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Токен подтверждения почты для пользователя {user}".format(user=self.user)
