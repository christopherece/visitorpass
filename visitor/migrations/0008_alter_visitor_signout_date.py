# Generated by Django 4.2.5 on 2023-09-21 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visitor', '0007_visitor_signout_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitor',
            name='signout_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
