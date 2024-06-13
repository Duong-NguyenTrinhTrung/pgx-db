from drug.models import DrugAtcAssociation, Drug, AtcTherapeuticGroup, AtcPharmacologicalGroup, AtcChemicalGroup, AtcChemicalSubstance, AtcAnatomicalGroup
from interaction.models import Interaction
import urllib.request
import os

#get the list of atc codes of a given length
def get_atc_code(length):
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

def get_drugs_belong_to_a_network(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    return undup_drugs

def createScriptToDownloadDataForPrecache(atc_code_length, filepath):
  atc_codes = get_atc_code(atc_code_length)
  print("atc_codes: ", atc_codes)
  with open(filepath, "w") as f:
    for atc_code in atc_codes:
      drugs = get_drugs_belong_to_a_network(atc_code)
      print(atc_code, " length drugs ", len(drugs))
      if len(drugs)>0:
        drug_link = "http://localhost:8000/drugs_network/drug_data?drug_bank_ids="
        protein_link = "http://localhost:8000/drugs_network/protein_data?drug_bank_ids="
        interaction_link = "http://localhost:8000/drugs_network/interaction_data?drug_bank_ids="
        general_link = "http://localhost:8000/drugs_network/general_data?drug_bank_ids="
        # drug_link = "https://pgx-db.org/drugs_network/drug_data?drug_bank_ids="
        # protein_link = "https://pgx-db.org/drugs_network/protein_data?drug_bank_ids="
        # interaction_link = "https://pgx-db.org/drugs_network/interaction_data?drug_bank_ids="
        # general_link = "https://pgx-db.org/drugs_network/general_data?drug_bank_ids="
        for drug in drugs[:-1]:
          drug_link = drug_link + drug+ ","
          protein_link = protein_link + drug+ ","
          interaction_link = interaction_link + drug+ ","
          general_link = general_link + drug+ ","
        drug_link = drug_link + drugs[-1]
        protein_link = protein_link + drugs[-1]
        interaction_link = interaction_link + drugs[-1]
        general_link = general_link + drugs[-1]
        f.write(atc_code+";"+drug_link+"\n")
        f.write(atc_code+";"+protein_link+"\n")
        f.write(atc_code+";"+interaction_link+"\n")
        f.write(atc_code+";"+general_link+"\n")

createScriptToDownloadDataForPrecache(1, "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/Data/linksToDownloadPrecachedData/Network_level1.txt")
createScriptToDownloadDataForPrecache(3, "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/Data/linksToDownloadPrecachedData/Network_level2.txt")
createScriptToDownloadDataForPrecache(4, "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/Data/linksToDownloadPrecachedData/Network_level3.txt")

def downloadAndSave(link_filename):
  with open(link_filename, "r") as f:
    lines = f.readlines()
    for line in lines:
      atc_code = line.split(";")[0]
      print(atc_code)
      if not os.path.exists("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/static/json-drug-network/"+atc_code):
          os.makedirs("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/static/json-drug-network/"+atc_code)
      link_to_download = line.split(";")[1]
      filename = ""
      try:
          print("link_to_download ", link_to_download)
          content = requests.get(link_to_download).content.decode('utf-8')
          if link_to_download.find("protein_data") > 0:
            filename = "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/static/json-drug-network/"+atc_code+"/protein_data.json"
          else:
            if link_to_download.find("drug_data") > 0:
              filename = "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/static/json-drug-network/"+atc_code+"/drug_data.json"
            else:
              if link_to_download.find("interaction_data") > 0:
                filename = "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/static/json-drug-network/"+atc_code+"/interaction_data.json"
              else:
                if link_to_download.find("general_data") > 0:
                  filename = "/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/static/json-drug-network/"+atc_code+"/general_data.json"
          with open(filename, "w") as file:
              file.write(content)
          print("Data has been successfully saved to ",filename, " length = ", len(content))
      except:
          print("Failed for ",filename)



downloadAndSave("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/Data/linksToDownloadPrecachedData/Network_level1.txt")   
downloadAndSave("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/Data/linksToDownloadPrecachedData/Network_level2.txt")   
downloadAndSave("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/ProjectBK-20230513/Data/linksToDownloadPrecachedData/Network_level3.txt")   