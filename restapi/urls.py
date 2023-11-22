from django.urls import path

from restapi.views import GeneDetailRestApiView, GeneDetailVepRestApiView, GeneDetailDrugRestApiView, AtcToTargetRestApiView, AtcToDescriptionRestApiView, AtcToPgxRestApiView

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
    path('gene/vep/<slug:gene_id>/', GeneDetailVepRestApiView, name='gene_detail_vep_RestApiView'),
    path('gene/drug/<slug:gene_id>/', GeneDetailDrugRestApiView, name='gene_detail_drug_RestApiView'),
    path('atc/target/<slug:atc_code>/', AtcToTargetRestApiView, name='atc_to_target_RestApiView'),
    path('atc/description/<slug:atc_code>/', AtcToDescriptionRestApiView, name='atc_to_description_RestApiView'),
    path('atc/pgx/<slug:atc_code_gene_id>/', AtcToPgxRestApiView, name='atc_to_pgx_RestApiView'),
]
