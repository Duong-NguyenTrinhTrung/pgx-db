from drug.models import DrugAtcAssociation, AtcChemicalGroup, AtcPharmacologicalGroup, AtcTherapeuticGroup, AtcChemicalSubstance, AtcAnatomicalGroup
from variant.models import GenebassVariantPGx
from interaction.models import Interaction
from drug.models import Drug
from disease.models import Disease, DrugDiseaseStudy
from django.db.models import Q

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import logging
import csv
import os
import pandas as pd

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="",
        )

    def handle(self, *args, **options):
        try:
            self.count_drug_protein_disease_nodes_level5()
            self.count_drug_protein_disease_nodes_level4()
            self.count_drug_protein_disease_nodes_level3()
            self.count_drug_protein_disease_nodes_level2()
            self.count_drug_protein_disease_nodes_level1()
        except Exception as msg:
            print(msg)

    def count_drug_protein_disease_nodes_level5(self):
        allChemicalSubstanceCodes = list(set(DrugAtcAssociation.objects.all().values_list("atc_id_id", flat=True)))
        with open("Data/StatisticForPlotting/Calculation_of_network_nodes_per_atc_level5_phase34.csv", "w") as f:
            f.write("ATC code;DrugNodes;ProteinNodes;InteractionEdges;DiseseNodes;AssociationEdges;TotalNodes;TotalEdges\n")
            for i,c in enumerate(allChemicalSubstanceCodes):
                # print(i, " ", c)
                drugs = list(set(DrugAtcAssociation.objects.filter(atc_id=c).select_related('drug_id').values_list("drug_id", flat=True)))
                gene_count = len(list(set(Interaction.objects.filter(drug_bankID__in=drugs).values_list("uniprot_ID__genename", flat=True))))
                interaction_count=len(Interaction.objects.filter(drug_bankID__in=drugs))
                disease_count = len(list(set(DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4"))).values_list("disease_name__disease_name", flat=True))))
                association_count=len(DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4"))))
                f.write(c + ";" + str(len(drugs)) + ";" + str(gene_count)+ ";" + str(interaction_count) + ";"+ str(disease_count) + ";"+ str(association_count) + ";"+str(len(drugs)+gene_count+disease_count)+";"+str(interaction_count+association_count)+"\n")

    def count_drug_protein_disease_nodes_level4(self):
        allChemicalGroupCodes = list(set(AtcChemicalGroup.objects.all().values_list("id", flat=True)))
        with open("Data/StatisticForPlotting/Calculation_of_network_nodes_per_atc_level4_phase34.csv", "w") as f:
            for i,cg in enumerate(allChemicalGroupCodes):
                drug_list=[]
                gene_list=[]
                disease_list=[]
                interaction_list=[]
                association_list=[]
                all_substance_codes = list(set(AtcChemicalSubstance.objects.filter(id__istartswith=cg).values_list("id", flat=True)))
                for i,sc in enumerate(all_substance_codes):
                    # drug
                    drugs = list(set(DrugAtcAssociation.objects.filter(atc_id=sc).select_related('drug_id').values_list("drug_id", flat=True)))
                    drug_list +=drugs
                    #gene
                    genes = list(set(Interaction.objects.filter(drug_bankID__in=drugs).values_list("uniprot_ID__genename", flat=True)))
                    gene_list+=genes
                    #interaction
                    interactions=Interaction.objects.filter(drug_bankID__in=drugs)
                    interaction_list+=interactions
                    #disease
                    diseases = list(set(DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4"))).values_list("disease_name__disease_name", flat=True)))
                    disease_list+=diseases
                    #association
                    associations=DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4")))
                    association_list+=associations

                drug_list=set(drug_list)
                gene_list=set(gene_list)
                disease_list=set(disease_list)
                interaction_list=set(interaction_list)
                association_list=set(association_list)

                f.write(cg + ";" + str(len(drug_list)) + ";" + str(len(gene_list))+ ";" + str(len(interaction_list)) + ";"+ str(len(disease_list)) + ";"+ str(len(association_list)) + ";"+str(len(drug_list)+len(gene_list)+len(disease_list))+";"+str(len(disease_list)+len(association_list))+"\n")


    def count_drug_protein_disease_nodes_level3(self):
        allPharmacologicalGroupCodes = list(set(AtcPharmacologicalGroup.objects.all().values_list("id", flat=True)))
        with open("Data/StatisticForPlotting/Calculation_of_network_nodes_per_atc_level3_phase34.csv", "w") as f:
            for i,pg in enumerate(allPharmacologicalGroupCodes):
                drug_list=[]
                gene_list=[]
                disease_list=[]
                interaction_list=[]
                association_list=[]
                all_substance_codes = list(set(AtcChemicalSubstance.objects.filter(id__istartswith=pg).values_list("id", flat=True)))
                for i,sc in enumerate(all_substance_codes):
                    # drug
                    drugs = list(set(DrugAtcAssociation.objects.filter(atc_id=sc).select_related('drug_id').values_list("drug_id", flat=True)))
                    drug_list +=drugs
                    #gene
                    genes = list(set(Interaction.objects.filter(drug_bankID__in=drugs).values_list("uniprot_ID__genename", flat=True)))
                    gene_list+=genes
                    #interaction
                    interactions=Interaction.objects.filter(drug_bankID__in=drugs)
                    interaction_list+=interactions
                    #disease
                    diseases = list(set(DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4"))).values_list("disease_name__disease_name", flat=True)))
                    disease_list+=diseases
                    #association
                    associations=DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4")))
                    association_list+=associations

                drug_list=set(drug_list)
                gene_list=set(gene_list)
                disease_list=set(disease_list)
                interaction_list=set(interaction_list)
                association_list=set(association_list)

                f.write(pg + ";" + str(len(drug_list)) + ";" + str(len(gene_list))+ ";" + str(len(interaction_list)) + ";"+ str(len(disease_list)) + ";"+ str(len(association_list)) + ";"+str(len(drug_list)+len(gene_list)+len(disease_list))+";"+str(len(disease_list)+len(association_list))+"\n")

    def count_drug_protein_disease_nodes_level2(self):
        allTherapeuticGroupCodes = list(set(AtcTherapeuticGroup.objects.all().values_list("id", flat=True)))
        with open("Data/StatisticForPlotting/Calculation_of_network_nodes_per_atc_level2_phase34.csv", "w") as f:
            for i,tg in enumerate(allTherapeuticGroupCodes):
                drug_list=[]
                gene_list=[]
                disease_list=[]
                interaction_list=[]
                association_list=[]
                all_substance_codes = list(set(AtcChemicalSubstance.objects.filter(id__istartswith=tg).values_list("id", flat=True)))
                for i,sc in enumerate(all_substance_codes):
                    # drug
                    drugs = list(set(DrugAtcAssociation.objects.filter(atc_id=sc).select_related('drug_id').values_list("drug_id", flat=True)))
                    drug_list +=drugs
                    #gene
                    genes = list(set(Interaction.objects.filter(drug_bankID__in=drugs).values_list("uniprot_ID__genename", flat=True)))
                    gene_list+=genes
                    #interaction
                    interactions=Interaction.objects.filter(drug_bankID__in=drugs)
                    interaction_list+=interactions
                    #disease
                    diseases = list(set(DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4"))).values_list("disease_name__disease_name", flat=True)))
                    disease_list+=diseases
                    #association
                    associations=DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4")))
                    association_list+=associations

                drug_list=set(drug_list)
                gene_list=set(gene_list)
                disease_list=set(disease_list)
                interaction_list=set(interaction_list)
                association_list=set(association_list)

                f.write(tg + ";" + str(len(drug_list)) + ";" + str(len(gene_list))+ ";" + str(len(interaction_list)) + ";"+ str(len(disease_list)) + ";"+ str(len(association_list)) + ";"+str(len(drug_list)+len(gene_list)+len(disease_list))+";"+str(len(disease_list)+len(association_list))+"\n")


    def count_drug_protein_disease_nodes_level1(self):
        allAnatomicalGroupCodes = list(set(AtcAnatomicalGroup.objects.all().values_list("id", flat=True)))
        with open("Data/StatisticForPlotting/Calculation_of_network_nodes_per_atc_level1_phase34.csv", "w") as f:
            for i,ag in enumerate(allAnatomicalGroupCodes):
                drug_list=[]
                gene_list=[]
                disease_list=[]
                interaction_list=[]
                association_list=[]
                all_substance_codes = list(set(AtcChemicalSubstance.objects.filter(id__istartswith=ag).values_list("id", flat=True)))
                for i,sc in enumerate(all_substance_codes):
                    # drug
                    drugs = list(set(DrugAtcAssociation.objects.filter(atc_id=sc).select_related('drug_id').values_list("drug_id", flat=True)))
                    drug_list +=drugs
                    #gene
                    genes = list(set(Interaction.objects.filter(drug_bankID__in=drugs).values_list("uniprot_ID__genename", flat=True)))
                    gene_list+=genes
                    #interaction
                    interactions=Interaction.objects.filter(drug_bankID__in=drugs)
                    interaction_list+=interactions
                    #disease
                    diseases = list(set(DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4"))).values_list("disease_name__disease_name", flat=True)))
                    disease_list+=diseases
                    #association
                    associations=DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&(Q(clinical_trial="3")|Q(clinical_trial="4")))
                    association_list+=associations

                drug_list=set(drug_list)
                gene_list=set(gene_list)
                disease_list=set(disease_list)
                interaction_list=set(interaction_list)
                association_list=set(association_list)

                f.write(ag + ";" + str(len(drug_list)) + ";" + str(len(gene_list))+ ";" + str(len(interaction_list)) + ";"+ str(len(disease_list)) + ";"+ str(len(association_list)) + ";"+str(len(drug_list)+len(gene_list)+len(disease_list))+";"+str(len(disease_list)+len(association_list))+"\n")

