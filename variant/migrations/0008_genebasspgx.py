# Generated by Django 4.2.7 on 2023-12-15 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gene', '0002_gene_primary_transcript'),
        ('drug', '0003_alter_atcanatomicalgroup_options_and_more'),
        ('variant', '0007_drugphenocode'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenebassPGx',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotation', models.CharField(default='', max_length=100)),
                ('n_cases', models.FloatField()),
                ('n_controls', models.FloatField()),
                ('coding_description', models.TextField(null=True)),
                ('Pvalue', models.FloatField()),
                ('Pvalue_Burden', models.FloatField()),
                ('Pvalue_SKAT', models.FloatField()),
                ('BETA_Burden', models.FloatField()),
                ('SE_Burden', models.FloatField()),
                ('drugbank_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drug.drug')),
                ('gene_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gene.gene')),
                ('phenocode', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='variant.variantphenocode')),
            ],
        ),
    ]
