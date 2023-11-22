from rest_framework.views import APIView
from rest_framework.response import Response

from gene.views import GeneDetailBaseView
from restapi.serializers import GeneDetailSerializer


class GeneDetailRestApiView(GeneDetailBaseView,APIView,):

    allowed_methods = ['get']

    def get(self, request, *args, **kwargs):
        serializer = GeneDetailSerializer(data=self.kwargs)

        if serializer.is_valid():
            data = self.get_gene_detail_data(serializer.validated_data.get('gene_id'))
            return Response(data)
        else:
            return Response(serializer.errors, status=400)


def GeneDetailVepRestApiView():
    pass

def GeneDetailDrugRestApiView():
    pass

def AtcToTargetRestApiView():
    pass

def AtcToDescriptionRestApiView():
    pass

def AtcToPgxRestApiView():
    pass
