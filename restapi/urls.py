from django.urls import path, re_path

from restapi.views import GeneVariantRestApiView, DrugByGeneRestApiView, TargetByAtcRestApiView, AtcToDescriptionRestApiView, \
                            AtcCodesByLevelRestApiView, TargetsByDrugRestApiView, GenebasedAssociationStatisticsRestApiView, AtcCodesByDrugRestApiView, AtcToPgxRestApiView, \
                            DrugTargetInteractionByAtcRestApiView, VariantToVepRestApiView, TargetToBundleRestApiView, DrugDiseaseAssociationByAtcRestApiView

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
    path('gene/variant/<slug:gene_id>/', GeneVariantRestApiView.as_view(), name='gene'),
    path('gene/drug/', DrugByGeneRestApiView.as_view(), name='drug_by_gene_RestApiView'),
    re_path('gene/associateStatictics/(?P<variant_marker>[a-zA-Z0-9_\-\/]+)', GenebasedAssociationStatisticsRestApiView.as_view(), name='genebased-association-statistics-RestApiView'),
    
    re_path('variant/VEPscore/(?P<variant_marker>[a-zA-Z0-9_\-\/]+)', VariantToVepRestApiView.as_view(), name='variant-to-VEP-RestApiView'),

    path('atc/target/<slug:atc_code>/', TargetByAtcRestApiView.as_view(), name='target-by-atc-RestApiView'),
    path('atc/interaction/<slug:atc_code>/', DrugTargetInteractionByAtcRestApiView.as_view(), name='drug-target-interaction-by-atc-RestApiView'),
    path('atc/association/<slug:atc_code>/', DrugDiseaseAssociationByAtcRestApiView.as_view(), name='drug-disease-association-by-atc-RestApiView'),
    path('atc/description/<slug:atc_code>/', AtcToDescriptionRestApiView.as_view(), name='atc-to-description-RestApiView'),
    path('atc/atc_code/<slug:atc_level>/', AtcCodesByLevelRestApiView.as_view(), name='atc-codes-by-level-RestApiView'),
    path('atc/pgx/<slug:atc_code>/', AtcToPgxRestApiView.as_view(), name='atc-to-pgx-RestApiView'),
    
    path('drug/target/<slug:drug_id>/', TargetsByDrugRestApiView.as_view(), name='targets-by-drug-RestApiView'),
    path('drug/atc_code/<slug:drug_id>/', AtcCodesByDrugRestApiView.as_view(), name='atc-codes-by-drug-RestApiView'),

    path('target/<slug:uniprot_id>/', TargetToBundleRestApiView.as_view(), name='bundle-data-by-target-RestApiView'),
]