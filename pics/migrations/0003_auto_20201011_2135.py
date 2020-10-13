# Generated by Django 3.1.2 on 2020-10-12 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pics', '0002_auto_20201005_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='media_type',
            field=models.CharField(choices=[('IMAGE', 'Image'), ('CAROUSEL_ALBUM', 'Carousel Album'), ('VIDEO', 'Video')], default='IMAGE', max_length=20),
        ),
        migrations.AlterModelTable(
            name='photo',
            table='photo',
        ),
    ]
