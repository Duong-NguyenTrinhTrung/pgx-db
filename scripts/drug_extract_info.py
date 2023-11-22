import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

import csv
from drug.models import Drug, DrugAtcAssociation

# Define the CSV file name
# csv_file = 'drug_data.csv'

# Define the headers for the CSV file
headers = ['drug_bankID', 'name', 'aliases', 'atc_id']

# Open the CSV file and write the headers
with open('/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Project/20230330-Alex_drug_atc_data.csv', 'w') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(headers)

    # Query the data from the models and write to the CSV file
    for drug in Drug.objects.all():
        associations = DrugAtcAssociation.objects.filter(drug_id=drug)
        for association in associations:
            data_row = [
                drug.drug_bankID,
                drug.name,
                drug.aliases,
                association.atc_id,
            ]
            writer.writerow(data_row)
