from variant.models import GenebassVariantPGx, VariantMapper, Pharmgkb
from django.db.models import Q
from gene.models import Gene
import matplotlib.pyplot as plt

rs_needed = Pharmgkb.objects.filter(Q(Variant_or_Haplotypes__startswith="rs")&Q(P_Value_numeric__lt=0.05)).values_list("Variant_or_Haplotypes", flat=True)
rs = list(rs_needed)
len(rs) #3612
mapping = VariantMapper.objects.filter(refseq__in=rs).values_list("ensembl", "refseq")
mapping.count() #1785

mapped_rs = []
for m in mapping:
    mapped_rs.append(m[1])

mapped_ensembl = []
for m in mapping:
    mapped_ensembl.append(m[0])


missing = [id for id in rs if id not in mapped_rs] #found that those are for rs id associated with non SNP, length = 137

mapped_genes = Pharmgkb.objects.filter(Variant_or_Haplotypes__in=mapped_rs).values_list("geneid_id", flat=True)
mapped_genenames = Gene.objects.filter(gene_id__in=mapped_genes).values_list("genename", flat=True)
mapped_genenames.count() #355
mapped_gbv = GenebassVariantPGx.objects.filter(genename__in=mapped_genenames)
mapped_gbv.count() #354913 - total, pharmgkb and non-pharmgkb

pharm_gbv =  GenebassVariantPGx.objects.filter(variant_marker__in=mapped_ensembl).values_list("Pvalue", "BETA")
pharm_gbv.count() #3198

non_pharm_gbv =  GenebassVariantPGx.objects.filter(Q(genename__in=mapped_genenames)&~Q(variant_marker__in=mapped_ensembl)).values_list("Pvalue", "BETA")
non_pharm_gbv.count() #351715


pharm_gbv_pvalues = []
pharm_gbv_betas = []
for t in pharm_gbv:
    pharm_gbv_pvalues.append(t[0])
    pharm_gbv_betas.append(t[1])

non_pharm_gbv_pvalues = []
non_pharm_gbv_betas = []
for t in non_pharm_gbv:
    non_pharm_gbv_pvalues.append(t[0])
    non_pharm_gbv_betas.append(t[1])


# Creating the boxplot
plt.boxplot([pharm_gbv_pvalues, non_pharm_gbv_pvalues], labels=['PharmgKB', 'Non PharmgKB'])
# Adding title and labels
plt.title('Comparison of Genebass associations with and without PharmgKB associations')
plt.ylabel('P_values')
# Displaying the plot
plt.show()


# Creating the boxplot
plt.boxplot([pharm_gbv_betas, non_pharm_gbv_betas], labels=['PharmgKB', 'Non PharmgKB'])
# Adding title and labels
plt.title('Comparison of Genebass associations with and without PharmgKB associations')
plt.ylabel('BETAs')
# Displaying the plot
plt.show()