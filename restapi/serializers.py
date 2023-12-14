from rest_framework import serializers

class GeneDetailSerializer(serializers.Serializer):
    # gene_id = serializers.CharField(
    #     required=True,
    # )
    pass
class VariantSerializer(serializers.Serializer):
    variant_marker = serializers.CharField(
        required=True,
    )
class AtcDetailSerializer(serializers.Serializer):
    print("check point 4")
    atc_code = serializers.CharField( #why atc_code_id not work?
        required=True,
    )
class AtcByLevelSerializer(serializers.Serializer):
    atc_level = serializers.CharField( 
        required=True,
    )

class TargetDrugSerializer(serializers.Serializer):
    drug_id = serializers.CharField( 
        required=True,
    )