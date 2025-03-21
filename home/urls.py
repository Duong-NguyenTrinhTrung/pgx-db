# from django.conf.urls import url
from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import Home, drug_target_network, drug_lookup, target_lookup, drug_autocomplete_view, protein_autocomplete_view, variant_autocomplete_view, variant_lookup, chromosome_mapper, variant_mapper, target_statistics, about_pgx, get_chromosome_mapping, get_variant_mapping, get_chromosome_mapping_example, get_variant_mapping_example, anno_from_autocomplete_view, variant_anno_from_autocomplete_view, disease_lookup, disease_statistics, disease_autocomplete_view, contribute_to_pgx, tutorial, get_se_definition, get_atc_code_statistics, adr_autocomplete_view, adr_lookup, use_case_examples


urlpatterns = [
    path("", cache_page(3600*24*7)(Home.as_view()), name='home'),
    path("about_pgx/", about_pgx, name='about-pgx'),
    path("contribute_to_pgx/", contribute_to_pgx, name='contribute-pgx'),

    path("drug_lookup/", cache_page(3600*24*365)(drug_lookup), name='drug-lookup'),
    path('drug-autocomplete/', drug_autocomplete_view, name='drug-autocomplete-view'),
    path("drug_target_network/", drug_target_network, name='drug-target-network'),
    path("get_se_definition/", get_se_definition, name='get-se-definition'),

    path("adr_lookup/", cache_page(3600*24*365)(adr_lookup), name='adr-lookup'),
    path('adr_autocomplete/', adr_autocomplete_view, name='adr-autocomplete-view'),

    path("target_lookup/", cache_page(3600*24*365)(target_lookup), name='target-lookup'),
    path("target_statistics/", cache_page(3600*24*365)(target_statistics), name='target-statistics'),
    path('protein-autocomplete/', protein_autocomplete_view, name='protein-autocomplete-view'),

    path("variant_lookup/", cache_page(3600*24*365)(variant_lookup), name='variant-lookup'),
    path("chromosome_mapper/", cache_page(3600*24*365)(chromosome_mapper), name='chromosome-mapper'),
    path("variant_mapper/", cache_page(3600*24*365)(variant_mapper), name='variant-mapper'),
    path("get_chromosome_mapping/", get_chromosome_mapping, name='get-chromosome-mapping'),
    path("get_variant_mapping/", get_variant_mapping, name='get-variant-mapping'),
    path("get_chromosome_mapping_example/", get_chromosome_mapping_example, name='get-chromosome-mapping-example'),
    path("get_variant_mapping_example/", get_variant_mapping_example, name='get-variant-mapping-example'),
    path("anno_from_autocomplete_view/", anno_from_autocomplete_view, name='anno-from-autocomplete-view'),
    path("variant_anno_from_autocomplete_view/", variant_anno_from_autocomplete_view, name='variant-anno-from-autocomplete-view'),
    path('variant-autocomplete/', variant_autocomplete_view, name='variant-autocomplete-view'),
    
    path("tutorial/", cache_page(3600*24*365)(tutorial), name='tutorial'),
    path("use_case_examples/", cache_page(3600*24*365)(use_case_examples), name='use-case-examples'),

    path('disease_lookup/', cache_page(3600*24*365)(disease_lookup), name='disease-lookup'),
    path('disease_statistics/', cache_page(3600*24*365)(disease_statistics), name='disease-statistics'),
    path('disease_autocomplete_view/', disease_autocomplete_view, name='disease-autocomplete-view'),

    path('get_atc_code_statistics/', cache_page(3600*24*365)(get_atc_code_statistics), name='get-atc-code-statistics'),
]
