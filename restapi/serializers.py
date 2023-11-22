from rest_framework import serializers


class GeneDetailSerializer(serializers.Serializer):
    gene_id = serializers.CharField(
        required=True,
    )
