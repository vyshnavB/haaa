# Generated by Django 4.1.3 on 2022-12-19 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0031_alter_user_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='cover',
            field=models.ImageField(default='card2.webp', upload_to='cover_img'),
        ),
    ]
