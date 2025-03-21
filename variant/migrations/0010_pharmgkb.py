# Generated by Django 4.0.8 on 2023-12-21 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drug', '0003_alter_atcanatomicalgroup_options_and_more'),
        ('gene', '0002_gene_primary_transcript'),
        ('variant', '0009_genebassvariantpgx'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pharmgkb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('VariantAnnotationID', models.CharField(max_length=100)),
                ('Variant_or_Haplotypes', models.TextField()),
                ('PMID', models.CharField(max_length=100)),
                ('Phenotype_Category', models.TextField()),
                ('Significance', models.TextField()),
                ('Notes', models.TextField()),
                ('Sentence', models.TextField()),
                ('Alleles', models.TextField()),
                ('P_Value', models.CharField(max_length=100)),
                ('Biogeographical_Groups', models.TextField()),
                ('Study_Type', models.CharField(max_length=100)),
                ('Study_Cases', models.FloatField()),
                ('Study_Controls', models.FloatField()),
                ('Direction_of_effect', models.TextField()),
                ('PD_PK_terms', models.TextField()),
                ('Metabolizer_types', models.TextField()),
                ('drugbank_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='drug.drug')),
                ('geneid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gene.gene')),
            ],
        ),
    ]
