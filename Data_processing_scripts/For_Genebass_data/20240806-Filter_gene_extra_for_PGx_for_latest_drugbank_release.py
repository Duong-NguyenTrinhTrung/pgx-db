import hail as hl
import pandas as pd

hl.init(local_tmpdir="/projects/ilfgrid/data/GeneBass/Variant_Data/tmp")
mt = hl.read_matrix_table("../variant_results.mt")
geneName_list = ['CYP7B1', 'SLC26A3', 'GPR17', 'GBA1',
       'EEF1A2', 'CYP7A1', 'PSCA', 'MYB', 'GPIHBP1', 'TSTD1', 'SLC13A4',
       'MAP2K4', 'PSEN1', 'AKT3', 'BAX', 'IL17F', 'ASGR1', 'NGFR', 'LAG3',
       'P2RX3', 'P2RX2', 'GIP', 'PMEL', 'FFAR2', 'IL1RL2', 'CD37', 'TLR6',
       'ITGB6', 'GPRC5D']

concerned_gene_names = hl.set(geneName_list)
subset = mt.filter_rows(concerned_gene_names.contains(mt.gene))
ht=subset.entries()
ht.export("/projects/ilfgrid/data/GeneBass/Variant_Data/GenebassDataFilteredFromAllDrugTargets/VariantLevel/20230205-Data_in_gene_csv/20240806-29-extra_genes.csv", delimiter=';;')
