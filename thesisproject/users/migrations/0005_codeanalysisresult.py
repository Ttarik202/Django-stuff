# Generated by Django 5.1.7 on 2025-04-04 17:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_codeupload_analysis_result'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeAnalysisResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('upload', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.codeupload')),
            ],
        ),
    ]
