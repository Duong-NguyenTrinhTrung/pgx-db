from django.db import models
from gene.models import Gene
from drug.models import Drug


class Variant(models.Model):
    VariantMarker = models.CharField(primary_key=True, max_length=255)
    Gene_ID = models.ForeignKey(
        "gene.gene", on_delete=models.CASCADE, default="None"
    )

class VariantMapper(models.Model):
    genome_version = models.CharField(max_length=50)
    ensembl = models.CharField(max_length=50)  # string values
    refseq = models.CharField(max_length=50)  # string values


class VariantPhenocode(models.Model):
    phenocode = models.CharField(primary_key=True, max_length=200)
    pheno_sex = models.CharField(max_length=100, default="None")
    description = models.TextField(null=True)
    description_more = models.TextField(null=True)

    def __str__(self):
        return "Phenocode: " + self.phenocode + "\n --- Description: " + self.description

    def to_json(self):
        return {
                "phenocode": self.phenocode, 
                "pheno_sex": self.pheno_sex, 
                "description": self.description, 
                "description_more": self.description_more, 
                }

class DrugPhenocode(models.Model):
    phenocode = models.ForeignKey("variant.VariantPhenocode", on_delete=models.CASCADE)
    coding_description = models.TextField(null=True)
    drugname_in_coding_description = models.CharField(max_length=100, null=True)
    


class VepVariant(models.Model):
    vep_id = models.AutoField(auto_created=True, primary_key=True)
    Variant_marker = models.ForeignKey(
        "variant.variant", on_delete=models.CASCADE
    )

    Transcript_ID = models.CharField(max_length=255)
    Consequence = models.CharField(max_length=255)
    cDNA_position = models.CharField(max_length=255)
    CDS_position = models.CharField(max_length=255)
    Protein_position = models.CharField(max_length=255)
    Amino_acids = models.CharField(max_length=255)
    Codons = models.CharField(max_length=255)
    Impact = models.CharField(max_length=50)
    Strand = models.IntegerField()
    # This code will create a float field that can store null values, which is the equivalent of NA in Django.
    AM_pathogenicity = models.FloatField(null=True)
    BayesDel_addAF_rankscore = models.FloatField()
    BayesDel_noAF_rankscore = models.FloatField()
    CADD_raw_rankscore = models.FloatField()
    ClinPred_rankscore = models.FloatField()
    DANN_rankscore = models.FloatField()
    DEOGEN2_rankscore = models.FloatField()
    Eigen_PC_raw_coding_rankscore = models.FloatField()
    Eigen_raw_coding_rankscore = models.FloatField()
    FATHMM_converted_rankscore = models.FloatField()
    GERP_RS_rankscore = models.FloatField()
    GM12878_fitCons_rankscore = models.FloatField()
    GenoCanyon_rankscore = models.FloatField()
    H1_hESC_fitCons_rankscore = models.FloatField()
    HUVEC_fitCons_rankscore = models.FloatField()
    LIST_S2_rankscore = models.FloatField()
    LRT_converted_rankscore = models.FloatField()
    M_CAP_rankscore = models.FloatField()
    MPC_rankscore = models.FloatField()
    MVP_rankscore = models.FloatField()
    MetaLR_rankscore = models.FloatField()
    MetaRNN_rankscore = models.FloatField()
    MetaSVM_rankscore = models.FloatField()
    MutPred_rankscore = models.FloatField()
    MutationAssessor_rankscore = models.FloatField()
    MutationTaster_converted_rankscore = models.FloatField()
    PROVEAN_converted_rankscore = models.FloatField()
    Polyphen2_HDIV_rankscore = models.FloatField()
    Polyphen2_HVAR_rankscore = models.FloatField()
    PrimateAI_rankscore = models.FloatField()
    REVEL_rankscore = models.FloatField()
    SIFT4G_converted_rankscore = models.FloatField()
    SIFT_converted_rankscore = models.FloatField()
    SiPhy_29way_logOdds_rankscore = models.FloatField()
    VEST4_rankscore = models.FloatField()
    bStatistic_converted_rankscore = models.FloatField()
    Fathmm_MKL_coding_rankscore = models.FloatField()
    Fathmm_XF_coding_rankscore = models.FloatField()
    Integrated_fitCons_rankscore = models.FloatField()
    PhastCons30way_mammalian_rankscore = models.FloatField()
    PhyloP30way_mammalian_rankscore = models.FloatField()
    LINSIGHT_rankscore = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['Transcript_ID']),
            models.Index(fields=['Variant_marker']),
        ]

#definition for pgx data from gene-based burden from Genebass
class GenebassPGx(models.Model):
    gene_id = models.ForeignKey(
        Gene,
        on_delete=models.CASCADE,
        null=True,
    )
    annotation = models.CharField(default="", max_length=100)
    n_cases = models.FloatField()
    n_controls = models.FloatField()
    phenocode = models.ForeignKey(
        VariantPhenocode,
        on_delete=models.CASCADE,
        null=True,
    )
    coding_description = models.TextField(null=True)
    Pvalue = models.FloatField()
    Pvalue_Burden = models.FloatField()
    Pvalue_SKAT = models.FloatField()
    BETA_Burden = models.FloatField()
    SE_Burden = models.FloatField()
    drugbank_id = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        null=True,
    )
    # class Meta:
    #     indexes = [
    #         models.Index(fields=['gene_id']),
    #     ]


#definition for pgx data from variant-based burden from Genebass
class GenebassVariantPGx(models.Model):
    genename = models.CharField(max_length=100)
    variant_marker = models.ForeignKey(Variant,
        on_delete=models.CASCADE,
        null=True,)
    annotation = models.CharField(max_length=100)
    n_cases = models.FloatField()
    n_controls = models.FloatField()
    phenocode = models.ForeignKey(
        VariantPhenocode,
        on_delete=models.CASCADE,
        null=True,
    )
    coding_description = models.TextField(null=True)
    description = models.TextField(null=True)
    AC = models.FloatField()
    AF = models.FloatField()
    Pvalue = models.FloatField()
    BETA = models.FloatField()
    drugbank_id = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['drugbank_id']),
            models.Index(fields=['genename']),
        ]

class GenebassCategory(models.Model):
    category_code = models.IntegerField(primary_key=True)
    category_description = models.TextField(null=True)

#genebass original data
class GenebassVariant(models.Model):
    gb_id = models.AutoField(auto_created=True, primary_key=True)
    markerID = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE
    )
    gene_id = models.ForeignKey(
        Gene,
        on_delete=models.CASCADE,
        null=True,
    )
    phenocode = models.ForeignKey(
        VariantPhenocode,
        on_delete=models.CASCADE,
        null=True,
    )
    n_cases = models.FloatField()
    n_controls = models.FloatField()
    n_cases_defined = models.FloatField()
    n_cases_both_sexes = models.FloatField()
    n_cases_females = models.FloatField()
    n_cases_males = models.FloatField()

    category = models.ForeignKey(
        GenebassCategory,
        on_delete=models.CASCADE,
        null=True,
    )
    AC = models.FloatField()
    AF = models.FloatField()
    BETA = models.FloatField()
    SE = models.FloatField()
    AF_Cases = models.FloatField()
    AF_Controls = models.FloatField()
    Pvalue = models.FloatField()

    # class Meta:
    #     indexes = [
    #         models.Index(fields=['gene_id']),
    #     ]


class Pharmgkb(models.Model):
    VariantAnnotationID = models.CharField(max_length=100)
    Variant_or_Haplotypes = models.TextField()
    PMID= models.CharField(max_length=100)
    Phenotype_Category = models.TextField()
    Significance = models.TextField()
    Notes = models.TextField()
    Sentence = models.TextField()
    Alleles = models.TextField()
    P_Value = models.CharField(max_length=100)
    P_Value_numeric = models.FloatField(null=True)
    Biogeographical_Groups = models.TextField()
    Study_Type = models.CharField(max_length=100)
    Study_Cases= models.FloatField()
    Study_Controls= models.FloatField()
    Direction_of_effect = models.TextField()
    PD_PK_terms = models.TextField()
    Metabolizer_types = models.TextField()
    drugbank_id = models.ForeignKey(
        Drug,
        on_delete=models.CASCADE,
        null=True,
    )
    geneid = models.ForeignKey(
        Gene,
        on_delete=models.CASCADE,
        null=True,
    )

class VariantStatistics(models.Model):
    # 'GeneID', 'TranscriptID', 'Chromosome', 'Total SNP', 'No_of__synonymous', 
    pass


