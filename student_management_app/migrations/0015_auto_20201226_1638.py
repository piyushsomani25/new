# Generated by Django 3.1 on 2020-12-26 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0014_auto_20201226_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentresult',
            name='cie_1',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studentresult',
            name='cie_2',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studentresult',
            name='cie_3',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studentresult',
            name='quiz_1',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studentresult',
            name='quiz_2',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studentresult',
            name='quiz_3',
            field=models.IntegerField(default=0),
        ),
    ]