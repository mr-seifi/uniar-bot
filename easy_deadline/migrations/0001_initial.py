# Generated by Django 4.1 on 2022-08-16 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('easy_vahed', '0004_course_majors'),
        ('prof', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exersice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('deadline', models.DateTimeField()),
                ('has_reminder', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='easy_vahed.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prof.student')),
            ],
        ),
    ]
