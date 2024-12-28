from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from gene.views import GeneDetailBaseView, DrugByGeneBaseView, GenebasedAssociationStatisticsView, BasicVariantAnnotationFromGeneIDView
from restapi.serializers import GeneDetailSerializer, AtcDetailSerializer, AtcByLevelSerializer, TargetDrugSerializer, VariantSerializer, TargetSerializer
from drug.views import DrugByAtcBaseView, DescriptionByAtcBaseView, AtcCodesByLevelBaseView, TargetsByDrugBaseView, AtcCodesByDrugView, PGxByAtcCodeView, \
                        DrugTargetInteractionByAtcBaseView, DrugDiseaseAssociationByAtcBaseView, AdrByDrugView, DiseaseAssociationByDrugView
from variant.views import VEPFromVariantBaseView
from protein.views import BundleByTargetCodeView
from django.core.cache import cache
from variant.models import GenebassCategory, VariantPhenocode
import pandas as pd


#Drug
class DrugToDiseaseAssociationRestApiView(DiseaseAssociationByDrugView, APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="Retrieves a comprehensive list of disease association studies for a specified drug, identified by its DrugBank ID. The data returned includes disease name, disease class, clinical trial phase, reference link",
            operation_summary="Get a list of disease association studies of a drug given a drugbank ID",
    )
    def get(self, request, *args, **kwargs):
        serializer = TargetDrugSerializer(data=self.kwargs)
        if serializer.is_valid():
            data = self.get_disease_association_by_drug(serializer.validated_data.get('drug_id'))
            return Response(data)
        else:
            return Response(serializer.errors, status=400)

class DrugToDrugAdrRestApiView(AdrByDrugView, APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="Retrieves a comprehensive list of adverse drug reaction for a specified drug, identified by its DrugBank ID. The data returned includes name of reaction a.k.a side effect, side effect definition, frequency of side effect in surveyed population",
            operation_summary="Get adverse drug reaction for a drug given its drugbank ID",
    )
    def get(self, request, *args, **kwargs):
        serializer = TargetDrugSerializer(data=self.kwargs)
        if serializer.is_valid():
            data = self.get_drug_adr_for_api(serializer.validated_data.get('drug_id'))
            return Response(data)
        else:
            return Response(serializer.errors, status=400)

class DrugByGeneRestApiView(DrugByGeneBaseView,APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="Retrieve a list of drugs that target a protein, or is carried, transported, catalyzed by a protein  identified by its encoding gene. Gene Ensembl ID or genename are acceptable input. Returned data include drug name, DrugBank identifiers, actions, known actions and mode of actions (Target, Carrier, Transporter or Enzyme).",
            operation_summary="Get a list of all drugs that interact with a protein given its encoding gene Ensembl ID or genename",
            manual_parameters=[openapi.Parameter('gene_id', openapi.IN_QUERY, description="gene_id", type=openapi.TYPE_STRING),
                               openapi.Parameter('genename', openapi.IN_QUERY, description="genename", type=openapi.TYPE_STRING)]
    )

    def get(self, request, *args, **kwargs):
        serializer = GeneDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            returned_data = []
            
            if request.GET.get('gene_id'):
                data = self.get_drug_by_gene_data(request.GET.get('gene_id'))
                name = request.GET.get('gene_id')
            else:
                if request.GET.get('genename'):
                    data = self.get_drug_by_gene_data(request.GET.get('genename'))
                    name = request.GET.get('genename')
                else:
                    return Response(serializer.errors, status=400)
                
            table_data = data.get('list_of_targeting_drug', [])
            if isinstance(table_data,list):
                return Response(table_data)
            else:
                if len(table_data)>0:
                    for index, row in table_data.iterrows():
                        d={
                            "drug_bankID":row["drug_bankID"],
                            "actions":row["actions"],
                            "known_action":row["known_action"],
                            "interaction_type":row["interaction_type"],
                        }
                        returned_data.append(d)
                    return Response({f"List of targeting drugs of gene {name}": returned_data})
                else:
                    return Response(serializer.errors, status=400)
        else:
            return Response(serializer.errors, status=400)

class DrugsByAtcRestApiView(DrugByAtcBaseView,APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="Retrieve a list of drugs associated with a given ATC code. Returned data include drug names and their DrugBank identifiers",
            operation_summary="Get a list of all drugs associated with a given ATC code",
    )

    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_drug_by_atc_code(serializer.validated_data.get('atc_code'))
            list_of_drugs = data.get('list_of_drugs', [])
            returned_data = []
            for drug in list_of_drugs:
                d={
                    "Drug name": drug.get("drugname"),
                    "DrugBank identifier": drug.get("DrugbankID"),
                }
                returned_data.append(d)
            if len(returned_data)>0:
                return Response({"List of drugs: ": returned_data})
            else:
                return Response({"List of drugs: ": "No results or wrong input. Please check it again!"})

        else:
            return Response(serializer.errors, status=400)

class DrugTargetInteractionByAtcRestApiView(DrugTargetInteractionByAtcBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="Retrieve a list of drug-protein interactions pairs where drugs associate with a given ATC code. Returned data include DrugBank identifiers, protein UniProt identifiers, actions, known actions and mode of actions",
            operation_summary="Get the list of drug-protein interations of a given ATC code",
    )
    
    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_interaction_by_atc_code(serializer.validated_data.get('atc_code'))
            interactions_by_atc_code = data.get('interactions_by_atc_code', [])
            atc_code = data.get('atc_code', "")
            if atc_code:
                atc_code = atc_code.upper()
            if len(interactions_by_atc_code)>0:
                return Response({f"List of drug-protein interations for {atc_code}": interactions_by_atc_code})
            else:
                return Response({f"List of drug-protein interations for {atc_code}": "No results or wrong input. Please check it again!"})

        else:
            return Response(serializer.errors, status=400)
        
class DrugDiseaseAssociationByAtcRestApiView(DrugDiseaseAssociationByAtcBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="Retrieve a list of drug-disease association studies where drugs associate with a given ATC code. Returned data include DrugBank identifiers, drug names, disease name, disease class, clinical trial phase of the association studies, external reference links, standard inchiKey.",
            operation_summary="Get the list of drug-indication associations of a given ATC code",
    )
    
    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_association_by_atc_code(serializer.validated_data.get('atc_code'))
            associations_by_atc_code = data.get('associations_by_atc_code', [])
            if associations_by_atc_code and associations_by_atc_code[0].get("Results")!=None:
                return Response(associations_by_atc_code)
            else:
                return Response({"List of drug-indication associations: ": associations_by_atc_code})
        else:
            return Response(serializer.errors, status=400)


#ATC code
class AtcToDescriptionRestApiView(DescriptionByAtcBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="Retrieve a description of a given ATC code",
            operation_summary="Get a description of a given ATC code",
    )
    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_description_by_atc_code(serializer.validated_data.get('atc_code'))
            description = data.get('description', [])
            atc_code = data.get('atc_code', "")
            return Response({f"ATC description for {atc_code}": description})
        else:
            return Response(serializer.errors, status=400)

class AtcCodesByLevelRestApiView(AtcCodesByLevelBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="Retrieve all ATC codes belonging to an ATC group. Please input 'A' for 'Anatomical', 'T' for 'Therapeutic', 'P' for 'Pharmacological', 'C' for 'Chemical', or 'CS' for 'Chemical substance'. Returned data include ",
            operation_summary="Get all ATC codes belonging to an ATC group",
    )

    def get(self, request, *args, **kwargs):
        serializer = AtcByLevelSerializer(data=self.kwargs)
        if serializer.is_valid():
            fullname = {
                        "a": 'Anatomical',
                        "t": 'Therapeutic',
                        "p": 'Pharmacological',
                        "c": 'Chemical',
                        "cs": 'ChemicalSubstance',
                        "A": 'Anatomical',
                        "T": 'Therapeutic',
                        "P": 'Pharmacological',
                        "C": 'Chemical',
                        "CS": 'ChemicalSubstance',
                        }
            data = self.get_atc_codes_by_level(self.kwargs.get("atc_level"))
            if fullname.get(serializer.validated_data.get('atc_level')):
                returned_data = []
                for pair in data.get("list_of_codes"):
                    temp = {
                        "ATC code": pair[0],
                        "Description": pair[1],
                    }
                    returned_data.append(temp)
                return Response({"All ATC codes in "+fullname.get(self.kwargs.get("atc_level"))+" group ": returned_data})
            else:
                return Response("Wrong input!")
        else:
            return Response(serializer.errors, status=400)

class AtcToPgxRestApiView(PGxByAtcCodeView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get PharmgKB pharmacogenomics data given an ATC code",
    )

    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_pharmgkb_pgx_by_atc_code(serializer.validated_data.get('atc_code'))
            Pharmacogenomics = data.get('pgx', [])
            atc_code = data.get('atc_code', "")
            if len(Pharmacogenomics)>0:
                return Response({f"ATC Pharmacogenomics for {atc_code}": Pharmacogenomics})
            else:
                return Response({f"ATC Pharmacogenomics for {atc_code}": "No results or wrong input. Please check it again!"})
        else:
            return Response(serializer.errors, status=400)

class AtcCodesByDrugRestApiView(AtcCodesByDrugView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get an ATC code of a drug given its drugbank ID",
    )

    def get(self, request, *args, **kwargs):
        serializer = TargetDrugSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_atc_codes_by_drug(serializer.validated_data.get('drug_id'))
            returned_data = data.get("list_of_atc_codes")
            print("returned_data ", returned_data)
            
            if len(returned_data)==1 and returned_data[0].get("Results")!=None:
                return Response(returned_data)
            else:
                temp=[{"Atc code": t.get("atc_code"), "Description": t.get("description")} for t in returned_data]
                return Response({"ATC code of drug "+self.kwargs.get("drug_id"): temp})
        else:
            return Response(serializer.errors, status=400)


#Gene/Target
class GenebasedAssociationStatisticsRestApiView(GenebasedAssociationStatisticsView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get variant association statistics given a variant identifier, i.e. 9_133445803_C/T",
    )

    def get(self, request, *args, **kwargs):
        serializer = VariantSerializer(data=self.kwargs)
        if serializer.is_valid():
            variant_marker = serializer.validated_data.get('variant_marker')
            variant_marker = variant_marker[:-1] if variant_marker[-1] == "/" else variant_marker
            data = self.get_association_statistics_by_variant_marker(variant_marker)

            if data.get("Results")!=None:
                # return Response(data, status=404)
                return Response(data)
            else:
                returned_data = []
                for index, row in data.get("association_statistics_data").iterrows():
                    temp = {
                        "Variant marker": row["markerID"],
                        "Phenotype description": row["phenocode"],
                        "n_cases": row["n_cases"],
                        "n_controls": row["n_controls"],
                        "n_cases_defined": row["n_cases_defined"],
                        "n_cases_both_sexes": row["n_cases_both_sexes"],
                        "n_cases_females": row["n_cases_females"],
                        "n_cases_males": row["n_cases_males"],
                        "Category": row["category"],
                        "AC": row["AC"],
                        "AF": row["AF"],
                        "BETA": row["BETA"],
                        "SE": row["SE"],
                        "AF_Cases": row["AF_Cases"],
                        "AF_Controls": row["AF_Controls"],
                        "Pvalue": row["Pvalue"],
                    }
                    returned_data.append(temp)
                return Response({"Gene-based association statistics of "+variant_marker: returned_data})
        else:
            return Response(serializer.errors, status=400)

class TargetToBundleRestApiView(BundleByTargetCodeView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get bundle data given a UniProt ID",
    )

    def get(self, request, *args, **kwargs):
        serializer = TargetSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_bundle_data_by_target(serializer.validated_data.get('uniprot_id'))
            return Response({"Bundle data:": data})
        else:
            return Response(serializer.errors, status=400)
    
class TargetsByDrugRestApiView(TargetsByDrugBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get a list of all proteins targeted by a drug given its drugbank ID",
    )

    def get(self, request, *args, **kwargs):
        serializer = TargetDrugSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_targets_by_drug(serializer.validated_data.get('drug_id')).get("list_of_targets")
            
            if len(data)==1 and type(data[0])=="list":
                return Response(data)
            else:
                returned_data = []
                for pair in data:
                    temp = {
                        "UniProt_ID": pair[0],
                        "Protein name": pair[1],
                        "Gene ID": pair[2],
                        "Gene name": pair[3],
                    }
                    returned_data.append(temp)
                return Response({"All targeted protein of "+self.kwargs.get("drug_id"): returned_data})
        else:
            return Response(serializer.errors, status=400)

#Variant
class VariantToVepRestApiView(VEPFromVariantBaseView, APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="Retrieves a list of variant effect prediction scores for a specified variant, identified by its identifier. The data returned includes 40 scores from different algorithms including AlphaMissense, pathogenicity, Polyphen2, SIFT",
            operation_summary="Get all VEP scores for a variant",
    )

    def get(self, request, *args, **kwargs):
        serializer = VariantSerializer(data=self.kwargs)
        if serializer.is_valid():
            data = self.get_vep_from_variant(serializer.validated_data.get('variant_marker'))
            return Response(data)
        else:
            return Response(serializer.errors, status=400)

class GeneVariantRestApiView(BasicVariantAnnotationFromGeneIDView,APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="Retrieves a list of variants occur in a specified variant, identified by its Enseml ID. The data returned includes transcript, consequence, cDNA position, CDS position, protein position, wildtype amino acid, mutant amino acid, respective codons, impact and allele frequency",
            operation_summary="Get basic annotations of all variants on a gene given its gene Enseml ID",
    )

    def get(self, request, *args, **kwargs):
        serializer = GeneDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            gene_data = self.get_basic_annotation_for_all_variant_by_gene(self.kwargs.get('gene_id'))
            # array_data = gene_data.get('array', [])
            # returned_data = []
            # for variant in array_data:
            #     d = {
            #         "Variant_marker": variant[0],
            #         "Transcript_ID": variant[1],
            #         "Consequence": variant[2],
            #         "cDNA_position": variant[3],
            #         "CDS_position": variant[4],
            #         "Protein_position": variant[5],
            #         "Amino_acids": variant[6],
            #         "Codons": variant[7],
            #         "Impact": variant[8],
            #     }
                
                # returned_data.append(d)
            return Response({'Basic information about variants of gene '+self.kwargs.get("gene_id"): gene_data})
        else:
            return Response(serializer.errors, status=400)
        
