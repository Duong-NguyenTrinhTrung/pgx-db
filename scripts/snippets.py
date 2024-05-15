#Create csv file including all drugs and its atc codes
with open(output_csv_file_path, 'w') as f:
    f.write('Drug Bank ID;Drug Type;Clinical_status;ATC ID\n')
    drugs = Drug.objects.all().values_list("drug_bankID", "drugtype", "Clinical_status")
    for i, drug in enumerate(drugs):
        print(drug)
        ass = list(DrugAtcAssociation.objects.filter(drug_id=drug).values_list("atc_id", flat=True))
        drug_bank_id = drug[0]
        drug_type = drug[1]
        clinical_status = drug[2]
        f.write(drug_bank_id+";"+str(drug_type)+";"+str(clinical_status)+";"+",".join(ass)+"\n")