# Generated by Django 5.0.6 on 2024-06-09 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LeetCodeUser',
            fields=[
                ('user_key', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50)),
                ('questions_solved', models.IntegerField()),
            ],
        ),
    ]