from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from gene.views import GeneDetailBaseView, DrugByGeneBaseView, GenebasedAssociationStatisticsView
from restapi.serializers import GeneDetailSerializer, AtcDetailSerializer, AtcByLevelSerializer, TargetDrugSerializer, VariantSerializer
from drug.views import TargetByAtcBaseView, DescriptionByAtcBaseView, AtcCodesByLevelBaseView, TargetsByDrugBaseView, AtcCodesByDrugView, PGxByAtcCodeView, \
                        DrugTargetInteractionByAtcBaseView
from variant.views import VEPFromVariantBaseView


class VariantToVepRestApiView(VEPFromVariantBaseView, APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get all VEP scores for a variant",
    )

    def get(self, request, *args, **kwargs):
        serializer = VariantSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_vep_from_variant(serializer.validated_data.get('variant_marker'))
            print(len(data))
            return Response(data)
        else:
            return Response(serializer.errors, status=400)

class GeneVariantRestApiView(GeneDetailBaseView,APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get a full annotation of all variants on a gene given its gene Enseml ID",
    )

    def get(self, request, *args, **kwargs):
        serializer = GeneDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            gene_data = self.get_gene_detail_data(serializer.validated_data.get('gene_id'))
            # print("gene_data: ", gene_data.keys())
            array_data = gene_data.get('array', [])
            print("type(array_data): ",type(array_data), " len of data ", len(array_data))
            returned_data = []
            for variant in array_data:
                d = {
                    "Variant_marker": variant[0],
                    "Transcript_ID": variant[1],
                    "Consequence": variant[2],
                    "cDNA_position": variant[3],
                    "CDS_position": variant[4],
                    "Protein_position": variant[5],
                    "Amino_acids": variant[6],
                    "Codons": variant[7],
                    "Impact": variant[8],
                }
                
                returned_data.append(d)
            return Response({'Basic information about the variant of gene '+self.kwargs: returned_data})
        else:
            return Response(serializer.errors, status=400)
        
class DrugByGeneRestApiView(DrugByGeneBaseView,APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get a list of all drugs that target a gene given its gene Ensembl ID or genename",
            manual_parameters=[openapi.Parameter('gene_id', openapi.IN_QUERY, description="gene_id", type=openapi.TYPE_STRING),
                               openapi.Parameter('genename', openapi.IN_QUERY, description="genename", type=openapi.TYPE_STRING)]
    )

    def get(self, request, *args, **kwargs):
        serializer = GeneDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            returned_data = []
                
            if request.GET.get('gene_id'):
                data = self.get_drug_by_gene_data(request.GET.get('gene_id'))
            else:
                if request.GET.get('genename'):
                    data = self.get_drug_by_gene_data(request.GET.get('genename'))
                else:
                    return Response(serializer.errors, status=400)
                
            table_data = data.get('list_of_targeting_drug', [])
            print("table_data : ", table_data)
            if len(table_data)>0:
                for index, row in table_data.iterrows():
                    print("row : ", row, "type : ", type(row))
                    d={
                        "drug_bankID":row["drug_bankID"],
                        "actions":row["actions"],
                        "known_action":row["known_action"],
                        "interaction_type":row["interaction_type"],

                    }
                    returned_data.append(d)
                return Response({"List of targeting drugs: ": returned_data})
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response(serializer.errors, status=400)

# class DrugByGeneRestApiView(DrugByGeneBaseView,APIView,):
#     allowed_methods = ['get']
#     @swagger_auto_schema(
#             operation_description="operation_description",
#             operation_summary="Get a list of all drugs that target a gene given its gene Ensembl ID",
#             manual_parameters=[openapi.Parameter('name', openapi.IN_QUERY, description="name", type=openapi.TYPE_STRING)]
#     )

#     def get(self, request, *args, **kwargs):
#         serializer = GeneDetailSerializer(data=self.kwargs)

#         if serializer.is_valid():
#             data = self.get_drug_by_gene_data(serializer.validated_data.get('gene_id'))
#             table_data = data.get('list_of_targeting_drug', [])
#             print("table_data : ", table_data)
#             returned_data = []
#             for index, row in table_data.iterrows():
#                 print("row : ", row, "type : ", type(row))
#                 d={
#                     "drug_bankID":row["drug_bankID"],
#                     "actions":row["actions"],
#                     "known_action":row["known_action"],
#                     "interaction_type":row["interaction_type"],

#                 }
#                 returned_data.append(d)
#             return Response({"List of targeting drugs: ": returned_data})
#         else:
#             return Response(serializer.errors, status=400)


class TargetByAtcRestApiView(TargetByAtcBaseView,APIView,):
    allowed_methods = ['get']
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get a list of all targets belonging to an ATC code",
    )

    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)
        print("checkpoint 5 in TargetByAtcRestApiView, self.kwargs = ", self.kwargs)
        print("checkpoint 5 in TargetByAtcRestApiView, serializer = ", serializer)

        if serializer.is_valid():
            print("checkpoint 6 when serializer is valid in TargetByAtcRestApiView")
            data = self.get_target_by_atc_code(serializer.validated_data.get('atc_code'))
            table_data = data.get('list_of_targets', [])
            returned_data = []
            for index, row in table_data.iterrows():
                d={
                    "DrugbankID":row["DrugbankID"],
                }
                returned_data.append(d)
            return Response({"List of targets: ": returned_data})
        else:
            print("checkpoint 7 when serializer is not valid in TargetByAtcRestApiView")
            return Response(serializer.errors, status=400)


class DrugTargetInteractionByAtcRestApiView(DrugTargetInteractionByAtcBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get the list of drug-protein interations of a given ATC code",
    )
    
    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_interaction_by_atc_code(serializer.validated_data.get('atc_code'))
            interactions_by_atc_code = data.get('interactions_by_atc_code', [])
            
            return Response({"List of drug-protein interations: ": interactions_by_atc_code})
        else:
            return Response(serializer.errors, status=400)
        
class AtcToDescriptionRestApiView(DescriptionByAtcBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get the description of an ATC code",
    )
    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_description_by_atc_code(serializer.validated_data.get('atc_code'))
            description = data.get('description', [])
            returned_data = [{
                    "Description":description,
                }]
            return Response({"ATC description: ": returned_data})
        else:
            return Response(serializer.errors, status=400)

class AtcCodesByLevelRestApiView(AtcCodesByLevelBaseView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get all ATC codes belonging to an ATC group",
    )

    def get(self, request, *args, **kwargs):
        serializer = AtcByLevelSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_atc_codes_by_level(serializer.validated_data.get('atc_level'))
            returned_data = []
            for pair in data.get("list_of_codes"):
                temp = {
                    "ATC code": pair[0],
                    "Description": pair[1],
                }
                returned_data.append(temp)
            return Response({"All ATC codes in "+self.kwargs.get("atc_level")+" group ": returned_data})
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
            data = self.get_targets_by_drug(serializer.validated_data.get('drug_id'))
            returned_data = []
            for pair in data.get("list_of_targets"):
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

class AtcToPgxRestApiView(PGxByAtcCodeView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get pharmacogenomics data given an ATC code",
    )

    def get(self, request, *args, **kwargs):
        serializer = AtcDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_pgx_by_atc_code(serializer.validated_data.get('atc_code'))
            Pharmacogenomics = data.get('pgx', [])
            returned_data = [{
                    "Pharmacogenomics":Pharmacogenomics,
                }]
            return Response({"ATC Pharmacogenomics: ": returned_data})
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
            returned_data = []
            for pair in data.get("list_of_atc_codes"):
                temp = {
                    "ATC code": pair.get("Atc code")[0],
                    "Description": pair.get("Description"),
                }
                returned_data.append(temp)
            return Response({"ATC code of drug "+self.kwargs.get("drug_id"): returned_data})
        else:
            return Response(serializer.errors, status=400)

class GenebasedAssociationStatisticsRestApiView(GenebasedAssociationStatisticsView,APIView,):
    allowed_method = ["get"]
    @swagger_auto_schema(
            operation_description="operation_description",
            operation_summary="Get gene-based association statistics given a gene Ensembl ID or gene name",
    )

    def get(self, request, *args, **kwargs):
        serializer = VariantSerializer(data=self.kwargs)
        if serializer.is_valid():
            data = self.get_association_statistics_by_variant_marker(serializer.validated_data.get('variant_marker'))
            if not data:
                return Response({"error" : f"{serializer.validated_data.get('variant_marker')[:-1]} not found"}, status=400)
            print("data = ",data)
            print("variant_marker = ",self.kwargs)
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
            return Response({"Gene-based association statistics of "+self.kwargs.get("variant_marker"): returned_data})
        else:
            return Response(serializer.errors, status=400)
