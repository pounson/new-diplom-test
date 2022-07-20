
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_alter_orderitems_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmemailtoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirm_email_tokens', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, который связан с этим токеном подтверждения почты'),
        ),
    ]
