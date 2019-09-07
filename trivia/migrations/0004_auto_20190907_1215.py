# Generated by Django 2.2.3 on 2019-09-07 16:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('trivia', '0003_room_host'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='socketticket',
            name='id',
        ),
        migrations.AlterField(
            model_name='socketticket',
            name='ticket',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
