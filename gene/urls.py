from django.urls import path, re_path
from .views import (
    GeneDetailBrowser,
    GenebassVariantListView,
    filter_gene_detail_page,
)

app_name = 'gene' # to distingush different app names when using url names

urlpatterns = [
    path('gene/<slug:slug>/', GeneDetailBrowser.as_view(), name='gene'),
    path('gene/<str:id>/filter', filter_gene_detail_page, name='filter-gene-detail-page'),
    path('gene/<str:pk>/genebass-variants/', GenebassVariantListView.as_view(), name='genebass-variants'),
    
]
