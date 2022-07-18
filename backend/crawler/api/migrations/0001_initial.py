# Generated by Django 4.0.4 on 2022-07-18 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=72)),
                ('url', models.CharField(max_length=2048)),
                ('crawl_duration', models.IntegerField(default=0)),
                ('last_crawl', models.DateTimeField(null=True)),
                ('status', models.IntegerField(default=4)),
            ],
            options={
                'ordering': ('title', 'url'),
            },
        ),
        migrations.CreateModel(
            name='WebsiteRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=256)),
                ('label', models.CharField(max_length=64)),
                ('interval', models.IntegerField()),
                ('active', models.BooleanField(default=False)),
                ('regex', models.CharField(max_length=128)),
                ('job_id', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ('url', 'interval'),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=64)),
                ('website_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.websiterecord')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=2048, null=True)),
                ('crawl_time', models.CharField(max_length=2048)),
                ('boundary_record', models.BooleanField(default=False)),
                ('url', models.CharField(max_length=2048)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.websiterecord')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=2048)),
                ('execution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.execution')),
            ],
        ),
        migrations.AddField(
            model_name='execution',
            name='website_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.websiterecord'),
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_node', to='api.node')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_node', to='api.node')),
            ],
        ),
    ]
