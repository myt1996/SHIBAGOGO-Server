# Generated by Django 2.2.1 on 2019-06-25 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_appuser_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appuser',
            name='qr',
        ),
    ]
