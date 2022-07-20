

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_alter_shops_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categories',
            old_name='shop',
            new_name='shops',
        ),
    ]
