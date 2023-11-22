# from django.conf.urls import url
from django.urls import path
from django.views.decorators.cache import cache_page
from .views import Home, drug_target_network, target_lookup, protein_autocomplete_view, variant_autocomplete_view, variant_lookup, variant_statistics, target_statistics


urlpatterns = [
    path("", Home.as_view(), name='home'),
    path("drug_target_network/", drug_target_network, name='drug_target_network'),
    path("target_lookup/", target_lookup, name='target_lookup'),
    path("variant_lookup/", variant_lookup, name='variant_lookup'),
    path("variant_statistics/", variant_statistics, name='variant_statistics'),
    path("target_statistics/", target_statistics, name='target_statistics'),
    path('protein-autocomplete/', protein_autocomplete_view, name='protein_autocomplete_view'),
    path('variant-autocomplete/', variant_autocomplete_view, name='variant_autocomplete_view'),
]
