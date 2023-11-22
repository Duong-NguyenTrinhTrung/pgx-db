from Bio.PDB import PDBList
import requests
import os
import csv

filename = '/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Data/protein_data/protein_data.csv' 
protein_IDs = []

with open(filename, 'r') as file:
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        protein_IDs.append(row['pk'])

# print(protein_IDs)

base_url = 'https://rest.uniprot.org/uniprotkb/{}.txt'

with open("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Data/protein_data/protein_seq_data.csv", "a") as f:
  for protein_ID in protein_IDs:
      print(protein_ID)
      url = base_url.format(protein_ID)
      response = requests.get(url)
      if response.status_code == 200:
              s = response.content
              seq=""
              for line in response.content.decode().splitlines():
                  if line.startswith("     "):
                        seq = seq + line
              f.write(protein_ID+","+seq.strip().replace(" ","")+"\n")
      else:
        print(f'Error: could not download sequence file for protein {protein_ID}')
