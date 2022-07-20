
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_rename_shop_categories_shops'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='order_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='backend.orders', verbose_name='Заказ'),
        ),
    ]
