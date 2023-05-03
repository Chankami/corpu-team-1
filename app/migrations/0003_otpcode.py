# Generated by Django 4.2 on 2023-05-02 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_login'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTPCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=5)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='codes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
