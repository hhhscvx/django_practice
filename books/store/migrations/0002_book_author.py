# Generated by Django 5.0.6 on 2024-06-03 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.CharField(default='author', max_length=255),
            preserve_default=False,
        ),
    ]
