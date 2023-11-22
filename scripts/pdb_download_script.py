from Bio.PDB import PDBList
import requests
import os
from os.path import exists
import csv

filename = '/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Project/Data/protein_data/protein_data.csv' # replace with the name of your CSV file
protein_IDs = []
uniprot_id_list = []

with open(filename, 'r') as file:
    reader = csv.DictReader(file, delimiter=',')
    for row in reader:
        protein_IDs.append(row['uniprot_ID'])

# print(protein_IDs)

base_url = 'https://alphafold.ebi.ac.uk/files/AF-{}-F1-model_v4.pdb'

for protein_ID in protein_IDs:
    url = base_url.format(protein_ID)
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Project/Data/protein_data/pdb/{protein_ID}.pdb', 'wb') as f:
            f.write(response.content)
    else:
        uniprot_id_list.append(protein_ID)
        print(f'Error: could not download PDB file for protein {protein_ID}')


#convert uniprot ID to pdb Id for those missing
# uniprot_id_list = ["P98164","P04275","Q07954","P98160","O60494","Q16881","Q9NZV6","P36969","P59796","P07203","P18283","P22352","P21817","P78527","Q13315","Q9UE69","P08519","Q92736","P78559","Q02817","P46939","P15924","Q86YZ3","P49908","Q13748","P04745","Q14643","Q5T4S7","Q8WXI7","P01266","Q9NNW7","Q02224","O15230","P25391","Q16787","P13611","P49895","Q92813","P55073","P42858","P35556","Q75N90","Q15413","P04114","P11532"]

# rs = {}
# uniprot_id = "P98164"
# pdir = '/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Data/pdb1'
# with open("/Users/ljw303/Duong_Data/Lab_Projects/PharmacogenomicsDB/Data/pdb1/list.txt", "w") as f:
#   for uniprot_id in uniprot_id_list:
#     url = f'https://www.uniprot.org/uniprot/{uniprot_id}.txt'
#     response = requests.get(url)
#     print(uniprot_id)
#     if response.status_code == 200:
#         for line in response.content.decode().splitlines():
#             if line.startswith('DR   PDB;'):
#                 pdb_id = line.split(';')[1].strip()
#                 # f.write(pdb_id+",")
#                 temp = rs.get(uniprot_id, [])
#                 temp.append(pdb_id)
#                 rs[uniprot_id] = temp
#                 # print(uniprot_id, " --> ", pdb_id)
#     else:
#         print(f'Error: could not retrieve PDB IDs for UniProt ID {uniprot_id}')
# print("results ", rs)

# for key in rs.keys():
#     print(key)
#     if os.path.exists(pdir+"/"+rs.get(key)+".pdb.gz"):
#         os.rename(pdir+"/"+rs.get(key)+".pdb.gz", pdir+"/"+key+".pdb")
#     else:
#         print(pdir+"/"+rs.get(key)+".pdb.gz NOT FOUND")