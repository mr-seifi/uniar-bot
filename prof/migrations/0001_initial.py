# Generated by Django 4.1 on 2022-08-14 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('easy_vahed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Major',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('cs', 'علوم کامپیوتر'), ('ce', 'مهندسی کامپیوتر'), ('math', 'ریاضیات و کاربردها'), ('electric', 'برق'), ('mechanic', 'مکانیک'), ('civil', 'عمران'), ('aerospace', 'هوافضا')], db_index=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('aut', 'امیرکبیر'), ('sut', 'شریف'), ('ut', 'تهران')], db_index=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('user_id', models.CharField(db_index=True, max_length=32)),
                ('user_name', models.CharField(max_length=128, null=True)),
                ('year', models.CharField(choices=[('98', 'ورودی 98'), ('99', 'ورودی 99'), ('00', 'ورودی 1400'), ('01', 'ورودی 1401')], max_length=8)),
                ('courses', models.ManyToManyField(to='easy_vahed.course')),
                ('major', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prof.major')),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prof.university')),
            ],
        ),
    ]
