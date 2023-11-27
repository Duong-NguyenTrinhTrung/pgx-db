from django.urls import path

from restapi.views import GeneDetailRestApiView, GeneDetailVepRestApiView, DrugByGeneRestApiView, TargetByAtcRestApiView, AtcToDescriptionRestApiView, \
                            AtcCodesByLevelRestApiView, TargetsByDrugRestApiView, GenebasedAssociationStatisticsRestApiView, AtcCodesByDrugRestApiView, AtcToPgxRestApiView

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        #  add your swagger doc title
        title="PGx API",
        #  version of the swagger doc
        default_version='v1',
        # first line that appears on the top of the doc
        description="Test description",
    ),
    public=True,
)


app_name = 'restapi'
urlpatterns = [
    path('gene/variant/<slug:gene_id>/', GeneDetailRestApiView.as_view(), name='gene'),
    path('gene/vep_score/<slug:gene_id>/', GeneDetailVepRestApiView.as_view(), name='gene_detail_vep_RestApiView'),
    path('gene/drug/<slug:gene_id>/', DrugByGeneRestApiView.as_view(), name='drug_by_gene_RestApiView'),
    path('atc/target/<slug:atc_code>/', TargetByAtcRestApiView.as_view(), name='target_by_atc_RestApiView'),
    path('atc/description/<slug:atc_code>/', AtcToDescriptionRestApiView.as_view(), name='atc_to_description_RestApiView'),
    path('atc/atc_code/<slug:atc_level>/', AtcCodesByLevelRestApiView.as_view(), name='atc_codes_by_level_RestApiView'),
    path('drug/target/<slug:drug_id>/', TargetsByDrugRestApiView.as_view(), name='targets_by_drug_RestApiView'),
    path('drug/atc_code/<slug:drug_id>/', AtcCodesByDrugRestApiView.as_view(), name='atc_codes_by_drug_RestApiView'),
    path('gene/associateStatictics/<slug:gene_id>/', GenebasedAssociationStatisticsRestApiView.as_view(), name='genebased_association_statistics_RestApiView'),
    path('atc/pgx/<slug:atc_code_gene_id>/', AtcToPgxRestApiView, name='atc_to_pgx_RestApiView'),
]
