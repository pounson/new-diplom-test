

import backend.models
from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('type', models.CharField(choices=[('shop', 'Магазин'), ('buyer', 'Покупатель')], default='buyer', max_length=10, verbose_name='Тип пользователя')),
                ('last_name', models.CharField(max_length=50, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=50, verbose_name='Имя')),
                ('patronymic', models.CharField(blank=True, max_length=50, verbose_name='Отчество')),
                ('company', models.CharField(blank=True, max_length=50, verbose_name='Компания')),
                ('position', models.CharField(blank=True, max_length=50, verbose_name='Должность')),
                ('username', models.CharField(blank=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, null=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='nickname')),
                ('is_active', models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Список пользователей',
                'db_table': 'users',
            },
            managers=[
                ('objects', backend.models.UsersManager()),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'db_table': 'categories',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Contacts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=100, verbose_name='Город')),
                ('street', models.CharField(max_length=100, verbose_name='Улица')),
                ('build', models.CharField(max_length=100, verbose_name='Дом')),
                ('corpus', models.CharField(blank=True, max_length=100, verbose_name='Корпус')),
                ('apartment', models.CharField(blank=True, max_length=100, verbose_name='Квартира')),
                ('phone', models.CharField(max_length=15, verbose_name='Номер телефона')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Контактные данные',
                'verbose_name_plural': 'Контактные данные',
                'db_table': 'contacts',
            },
        ),
        migrations.CreateModel(
            name='Parameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название параметра')),
            ],
            options={
                'verbose_name': 'Имя параметра',
                'verbose_name_plural': 'Имена параметров',
                'db_table': 'parameters',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название товара')),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='backend.categories', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Список продуктов',
                'db_table': 'products',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Shops',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название магазина')),
                ('url_shop', models.CharField(blank=True, max_length=50)),
                ('status_work', models.BooleanField(default=True, verbose_name='Статус приёма заказов')),
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_id', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Магазины',
                'db_table': 'shops',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='ProductsInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.PositiveIntegerField(null=True, verbose_name='Внешний ИД')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('price', models.PositiveIntegerField(verbose_name='Цена')),
                ('price_rrc', models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.products', verbose_name='Товар')),
                ('shop_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.shops', verbose_name='Магазины')),
            ],
            options={
                'verbose_name': 'Информация о продукте',
                'verbose_name_plural': 'Информация о продуктах',
                'db_table': 'products_info',
            },
        ),
        migrations.CreateModel(
            name='ProductParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100, verbose_name='Значение параметра')),
                ('parameter_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='backend.parameters', verbose_name='Параметр')),
                ('product_info_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='backend.productsinfo', verbose_name='Информация о продукте')),
            ],
            options={
                'verbose_name': 'Параметр продукта',
                'verbose_name_plural': 'Список параметров продукта',
                'db_table': 'product_parameter',
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('basket', 'Статус корзины'), ('new', 'Новый'), ('confirmed', 'Подтвержден'), ('assembled', 'Собран'), ('sent', 'Отправлен'), ('delivered', 'Доставлен'), ('canceled', 'Отменен')], max_length=20, verbose_name='Статус')),
                ('contact', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.contacts', verbose_name='Контакт')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='backend.orders', verbose_name='Заказ')),
                ('product_info_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='backend.productsinfo', verbose_name='Информация о продукте')),
            ],
            options={
                'verbose_name': 'Заказанный товар',
                'verbose_name_plural': 'Список заказанных товаров',
            },
        ),
        migrations.CreateModel(
            name='ConfirmEmailToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='When was this token generated')),
                ('key', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Key')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirm_email_tokens', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, который связан с этим токеном сброса пароля')),
            ],
            options={
                'verbose_name': 'Токен подтверждения Email',
                'verbose_name_plural': 'Токены подтверждения Email',
            },
        ),
        migrations.AddField(
            model_name='categories',
            name='shop',
            field=models.ManyToManyField(related_name='categories', to='backend.Shops', verbose_name='Магазины'),
        ),
        migrations.AddConstraint(
            model_name='productsinfo',
            constraint=models.UniqueConstraint(fields=('product_id', 'shop_id', 'external_id'), name='unique_product_info'),
        ),
        migrations.AddConstraint(
            model_name='productparameter',
            constraint=models.UniqueConstraint(fields=('product_info_id', 'parameter_id'), name='unique_product_parameter'),
        ),
        migrations.AddConstraint(
            model_name='orderitems',
            constraint=models.UniqueConstraint(fields=('order_id', 'product_info_id'), name='unique_order_item'),
        ),
    ]
