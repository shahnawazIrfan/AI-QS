# Generated by Django 3.1.12 on 2025-04-15 05:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskRegisterSection',
            fields=[
                ('_id', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Risk Register Section',
            },
        ),
        migrations.CreateModel(
            name='RiskRegister',
            fields=[
                ('_id', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('ref', models.CharField(blank=True, max_length=100, null=True)),
                ('risk_category', models.TextField(blank=True, null=True)),
                ('specific_risk', models.TextField(blank=True, null=True)),
                ('risk_owner', models.CharField(blank=True, max_length=100, null=True)),
                ('likelihood', models.IntegerField(blank=True, null=True)),
                ('impact', models.IntegerField(blank=True, null=True)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('mitigation', models.TextField(blank=True, null=True)),
                ('mitigated_likelihood', models.IntegerField(blank=True, null=True)),
                ('mitigated_impact', models.IntegerField(blank=True, null=True)),
                ('mitigated_rating', models.FloatField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('cost', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='risk_register', to='web_app.riskregistersection')),
            ],
            options={
                'verbose_name_plural': 'Risk Register',
            },
        ),
    ]
