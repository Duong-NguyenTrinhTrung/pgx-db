from django.urls import path, re_path
from .views import (
    # GenebassVariantListView,
    filter_gene_detail_page,
    get_gene_detail_data,
    get_variant_annotation_and_vep
)

app_name = 'gene' # to distingush different app names when using url names

urlpatterns = [
    path('gene/gene_detail/<slug:slug>/', get_gene_detail_data, name='get-gene-detail-data'),
    path('gene/vaav/<slug:slug>/', get_variant_annotation_and_vep, name='get-variant-annotation-and-vep'),
    
]
