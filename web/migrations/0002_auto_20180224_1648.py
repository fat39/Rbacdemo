# Generated by Django 2.0.1 on 2018-02-24 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='ptime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
