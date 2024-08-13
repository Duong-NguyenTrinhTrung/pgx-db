import pandas as pd
import os

#os.mkdir("/maps/projects/ilfgrid/data/GeneBass/Variant_Data/GenebassDataFilteredFromAllDrugTargets/VariantLevel/20240811-Data_in_gene_csv_in_format_for_putting_in_database")
scr="/maps/projects/ilfgrid/data/GeneBass/Variant_Data/GenebassDataFilteredFromAllDrugTargets/VariantLevel/20230905-Data_in_gene_selected_categories_csv"
des="/maps/projects/ilfgrid/data/GeneBass/Variant_Data/GenebassDataFilteredFromAllDrugTargets/VariantLevel/20240811-Data_in_gene_csv_in_format_for_putting_in_database"
filenames = ["AKT3.csv", "ASGR1.csv", "BAX.csv", "CD37.csv", "CDH11.csv", "CYP7A1.csv", "CYP7B1.csv", "EEF1A2.csv", "FFAR2.csv", "GBA1.csv", "GIP.csv", "GPIHBP1.csv", "GPR17.csv", "GPRC5D.csv", "IL17F.csv", "IL1RL2.csv", "ITGB6.csv", "LAG3.csv", "MAP2K4.csv", "MYB.csv", "NGFR.csv", "P2RX2.csv", "P2RX3.csv", "PMEL.csv", "PRIM1.csv", "PSCA.csv", "PSEN1.csv", "SLC13A4.csv", "SLC26A3.csv", "SLC7A10.csv", "TLR6.csv", "TSTD1.csv"]
i=0
for idx, filename in enumerate(filenames):
  print(idx, " ", filename)
  try:
    df = pd.read_csv(scr+"/"+filename, sep=";;")
    df.columns = ["locus", "alleles", "markerID", "gene", "annotation", "call_stats", "n_cases", "n_controls", "heritability", "saige_version", "inv_normalized", "trait_type", "phenocode", "pheno_sex", "coding", "modifier", "n_cases_defined", "n_cases_both_sexes", "n_cases_females", "n_cases_males", "description", "description_more", "coding_description", "category", "AC", "AF", "BETA", "SE", "AF.Cases", "AF.Controls", "Pvalue" ]
    df = df [["n_cases", "n_controls", "n_cases_defined", "n_cases_both_sexes", "n_cases_females", "n_cases_males",  "AC", "AF", "BETA", "SE", "AF.Cases", "AF.Controls", "Pvalue", "category", "markerID", "phenocode", "gene"]]
    df.to_csv(des+"/"+filename, sep=";", index=False)
  except:
    print("file has exception ", filename) 
