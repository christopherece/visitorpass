# Generated by Django 4.2.5 on 2023-09-21 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitor', '0005_visitor_is_signout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitor',
            name='is_signout',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]