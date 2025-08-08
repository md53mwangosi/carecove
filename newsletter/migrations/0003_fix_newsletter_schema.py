# Generated manually to fix newsletter schema issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0002_alter_newsletter_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='is_pending_approval',
            field=models.BooleanField(default=True),
        ),
    ]