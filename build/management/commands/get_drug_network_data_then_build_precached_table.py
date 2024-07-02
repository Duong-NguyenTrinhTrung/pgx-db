from django.core.management.base import BaseCommand
from drug.services import DrugNetworkGetDataService, DrugsNetworkGetDataService
from django.db import transaction
import json
from drug.models import DrugAtcAssociation, Drug, AtcTherapeuticGroup, AtcPharmacologicalGroup, AtcChemicalGroup, AtcChemicalSubstance, AtcAnatomicalGroup
from interaction.models import Interaction
import urllib.request
import os
from drug.models import PreCachedDrugNetwork





class Command(BaseCommand):
    help = 'Process data from raw file to database and use DrugNetworkGetDataService'

    def handle(self, *args, **kwargs):
        try:
            self.purge_precached_drug_network_classs()
            self.process_raw_data()
        except Exception as msg:
            print(msg)

    def purge_precached_drug_network_classs(self):
        try:
            PreCachedDrugNetwork.objects.all().delete()
        except PreCachedDrugNetwork.DoesNotExist:
            self.logger.warning("PreCachedDrugNetwork mod not found: nothing to delete.")

    #get the list of atc codes of a given length
    def get_atc_code_list(self, length):
        if length==7:  
            return list(AtcChemicalSubstance.objects.all().values_list('id', flat=True))
        else:
            if length == 5:  
                return list(AtcChemicalGroup.objects.all().values_list('id', flat=True))
            else:
                if length == 4:  
                    return list(AtcPharmacologicalGroup.objects.all().values_list('id', flat=True))
                else:
                    if length == 3:  
                        return list(AtcTherapeuticGroup.objects.all().values_list('id', flat=True))
                    else:
                        if length == 1:
                            return list(AtcAnatomicalGroup.objects.all().values_list('id', flat=True))
                        else:
                            return []

    def get_list_of_drugs_belong_to_a_network(self, atc_code):
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        return undup_drugs
        
    def process_raw_data(self):
        atc_code_lengths = [3,4]
        for length in atc_code_lengths:
            list_of_atc_codes = self.get_atc_code_list(length)
            for atc_code in [x for x in list_of_atc_codes if x not in ["S01", "L01", "L01X"]]: 
                print(atc_code)
                list_of_drugs = self.get_list_of_drugs_belong_to_a_network(atc_code)
                print("list_of_drugs ", list_of_drugs)
                # Initialize the DrugNetworkGetDataService
                if len(list_of_drugs)>1:
                    print("use DrugsNetworkGetDataService")
                    service = DrugsNetworkGetDataService(drug_bank_ids=list_of_drugs)
                    # Fetch drug data
                    drug_network_data = service.get_drug_data2()
                    json_drug_string = json.dumps(drug_network_data, indent=4)
                else:
                    if len(list_of_drugs)==1:
                        print("use DrugNetworkGetDataService")
                        try:
                            drug = Drug.objects.get(drug_bankID=list_of_drugs[0])
                            service = DrugNetworkGetDataService(drug=drug)
                            # Fetch drug data
                            drug_network_data = service.get_drug_data()
                            json_drug_string = json.dumps(drug_network_data, indent=4)
                        except Drug.DoesNotExist:
                            raise Http404("Drug does not exist")
                        
                
                # Fetch protein data
                protein_network_data = service.get_protein_data()
                json_protein_string = json.dumps(protein_network_data, indent=4)
                # Fetch interaction data
                interaction_network_data = service.get_interaction_data()
                json_interaction_string = json.dumps(interaction_network_data, indent=4)
                # Fetch general data
                general_network_data = service.get_general_data()
                json_general_string = json.dumps(general_network_data, indent=4)

                # PreCachedDrugNetwork.objects.create(
                #     atc_code=atc_code,
                #     drug_json_data=drug_network_data,
                #     protein_json_data=protein_network_data,
                #     general_json_data=interaction_network_data,
                #     interaction_json_data=general_network_data,
                #     )
                PreCachedDrugNetwork.objects.create(
                    atc_code=atc_code,
                    drug_json_data=json_drug_string,
                    protein_json_data=json_protein_string,
                    general_json_data=json_general_string,
                    interaction_json_data=json_interaction_string,
                    )


