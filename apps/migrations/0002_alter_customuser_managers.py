# Generated by Django 4.1.3 on 2022-12-25 14:41

import apps.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', apps.managers.UserManager()),
            ],
        ),
    ]