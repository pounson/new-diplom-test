

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shops',
            name='url_shop',
            field=models.URLField(blank=True, max_length=50, verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='shops',
            name='user_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_id', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
