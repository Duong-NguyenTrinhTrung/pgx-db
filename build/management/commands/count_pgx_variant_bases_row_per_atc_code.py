# your_app/management/commands/count_variants.py

from django.core.management.base import BaseCommand
from variant.models import VepVariant, GenebassVariantPGx
from drug.models import DrugAtcAssociation, Drug, AtcAnatomicalGroup, AtcTherapeuticGroup, AtcPharmacologicalGroup, AtcChemicalGroup, AtcChemicalSubstance
from interaction.models import Interaction

class Command(BaseCommand):
    def count_per_atc_codes_per_group(self, rsFile, length, allChemicalSubstanceCodes):

        if length == 1:
            atc_codes = list(AtcAnatomicalGroup.objects.all().values_list('id', flat=True))
        elif length == 3:
            atc_codes = list(AtcTherapeuticGroup.objects.all().values_list('id', flat=True))
        elif length == 4:
            atc_codes = list(AtcPharmacologicalGroup.objects.all().values_list('id', flat=True))
        elif length == 5:
            atc_codes = list(AtcChemicalGroup.objects.all().values_list('id', flat=True))
        else:
            atc_codes = list(AtcChemicalSubstance.objects.all().values_list('id', flat=True))

        print("length = ", length, " -->  ",atc_codes)
        
    
        with open(rsFile, "a") as f:
            for atc_code in atc_codes:
                
                chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
                drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
                undup_drugs = list(set(drugs))
                drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
                gene_names = list(set(Interaction.objects.filter(drug_bankID__in=undup_drugs).values_list("uniprot_ID__genename", flat=True)))
                response_data=[]
                count = 0
                for drug in drug_objs:
                    genebass_data = GenebassVariantPGx.objects.filter(
                        drugbank_id=drug, genename__in=gene_names
                    )
                    if len(genebass_data) != 0:
                        count+= len(genebass_data)
                f.write(f"\"{atc_code}\": {str(count)},\n")


    def handle(self, *args, **kwargs):
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        rsFile = "static/static_data/atc_pgx_variant_count.json"
        for length in [1,3,4,5,7]:
            self.count_per_atc_codes_per_group(rsFile, length, allChemicalSubstanceCodes) # after this, manually add { and } at the begining and end of file to make it a json format
        