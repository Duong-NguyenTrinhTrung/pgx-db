# from django.conf.urls import url
from django.urls import path
from django.views.decorators.cache import cache_page
from .views import Home, drug_target_network, drug_lookup, target_lookup, drug_autocomplete_view, protein_autocomplete_view, variant_autocomplete_view, variant_lookup, chromosome_mapper, target_statistics, about_pgx, get_chromosome_mapping, get_chromosome_mapping_example, anno_from_autocomplete_view


urlpatterns = [
    path("", cache_page(3600*24*7)(Home.as_view()), name='home'),
    path("drug_target_network/", drug_target_network, name='drug_target_network'),
    path("drug_lookup/", cache_page(3600*24*7)(drug_lookup), name='drug_lookup'),
    path("about_pgx/", about_pgx, name='about-pgx'),
    path("target_lookup/", cache_page(3600*24*7)(target_lookup), name='target_lookup'),
    path("variant_lookup/", cache_page(3600*24*7)(variant_lookup), name='variant_lookup'),
    path("chromosome_mapper/", chromosome_mapper, name='chromosome_mapper'),
    path("get_chromosome_mapping/", get_chromosome_mapping, name='get_chromosome_mapping'),
    path("get_chromosome_mapping_example/", get_chromosome_mapping_example, name='get_chromosome_mapping_example'),
    path("anno_from_autocomplete_view/", anno_from_autocomplete_view, name='anno-from-autocomplete-view'),
    path("target_statistics/", target_statistics, name='target_statistics'),
    path('protein-autocomplete/', protein_autocomplete_view, name='protein_autocomplete_view'),
    path('drug-autocomplete/', drug_autocomplete_view, name='drug_autocomplete_view'),
    path('variant-autocomplete/', variant_autocomplete_view, name='variant_autocomplete_view'),
]
