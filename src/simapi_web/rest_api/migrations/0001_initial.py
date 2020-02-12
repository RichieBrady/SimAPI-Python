# Generated by Django 3.0.2 on 2020-02-12 00:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InitModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=255, unique=True)),
                ('step_size', models.IntegerField(default=0)),
                ('final_time', models.DecimalField(decimal_places=1, max_digits=20)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Output',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_step', models.BigIntegerField(default=0, unique=True)),
                ('yshade', models.DecimalField(decimal_places=4, max_digits=20)),
                ('dry_bulb', models.DecimalField(decimal_places=4, max_digits=20)),
                ('troo', models.DecimalField(decimal_places=4, max_digits=20)),
                ('isolext', models.DecimalField(decimal_places=4, max_digits=20)),
                ('sout', models.DecimalField(decimal_places=4, max_digits=20)),
                ('zonesens', models.DecimalField(decimal_places=4, max_digits=20)),
                ('cool_rate', models.DecimalField(decimal_places=4, max_digits=20)),
                ('model_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.InitModel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_step', models.BigIntegerField(default=0, unique=True)),
                ('yshade', models.DecimalField(decimal_places=4, max_digits=20)),
                ('model_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.InitModel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
