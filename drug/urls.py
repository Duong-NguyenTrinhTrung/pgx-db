from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import selection_autocomplete, get_drug_statistics
from . import views
from .views import (
    search_drugs, drug_atc_expansion, atc_lookup, 
    atc_detail_view, atc_search_view, 
    get_drug_atc_association, get_drug_network, get_drugs_network, 
    get_statistics_by_atc, get_gene_based_burden_data_by_atc, get_variant_based_burden_data_by_atc, get_clinical_pgx_data_by_atc, 
    get_clinical_pgx_data_by_drug, 
    get_data_for_comparing_network_degree_distribution, 
    get_data_for_comparing_common_and_unique_network_element, 
    get_statistics_by_atc_for_network_size_comparison, 
    get_statistics_by_atc_for_clinical_trial_phase_comparison, 
    get_statistics_by_atc_code_for_MOA_comparison, 
    get_data_for_comparing_network_associate_distribution, 
    get_statistics_by_atc_for_measure_centralization_drug_disease, 
    get_statistics_by_atc_for_measure_centralization_drug_protein, 
    get_statistics_by_atc_for_detecting_community_drug_protein, 
    get_statistics_by_atc_for_detecting_community_drug_disease, 
    get_statistics_by_atc_for_calculating_average_path_length_drug_disease,
    get_statistics_by_atc_for_calculating_average_path_length_drug_protein,
    atc_comparison_autocomplete_view
)

urlpatterns = [
    path('search_drugs', views.search_drugs, name='search_drugs'),
    path('atc_lookup', cache_page(3600*24*365)(views.atc_lookup), name='atc-lookup'),
    path('atc_anatomical_groups', views.AtcAnatomicalGroupListView.as_view(), name='atc-anatomical-groups'),
    path('atc_search_view', cache_page(3600*24*365)(views.atc_search_view), name='atc-search-view'),

    path('atc_detail_view/', views.atc_detail_view, name='atc-detail-view'),
    path('get_drug_atc_association/', views.get_drug_atc_association, name='get-drug-atc-association'),
    path('get_drug_association/', views.get_drug_association, name='get-drug-association'),
    path('get_drug_list_by_uniprotID/', views.get_drug_list_by_uniprotID, name='get-drug-list-by-uniprotID'),
    path('get_statistics_by_atc/', views.get_statistics_by_atc, name='get-statistics-by-atc'),
    path('get_clinical_pgx_data_by_atc/', views.get_clinical_pgx_data_by_atc, name='get-clinical-pgx-data-by-atc'),
    path('get_clinical_pgx_data_by_drug/', views.get_clinical_pgx_data_by_drug, name='get-clinical-pgx-data-by-drug'),
    path('get_gene_based_burden_data_by_atc/', views.get_gene_based_burden_data_by_atc, name='get-gene-based-burden-data-by-atc'),
    path('get_variant_based_burden_data_by_atc/', views.get_variant_based_burden_data_by_atc, name='get-variant-based-burden-data-by-atc'),
    path('get_variant_based_burden_data_by_drug/', views.get_variant_based_burden_data_by_drug, name='get-variant-based-burden-data-by-drug'),
    path('get_gene_based_burden_data_by_drug/', views.get_gene_based_burden_data_by_drug, name='get-gene-based-burden-data-by-drug'),
    path('get_drug_network/', views.get_drug_network, name='get-drug-network'),
    path('get_atc_sub_levels/', views.get_atc_sub_levels, name='get-atc-sub-levels'),
    path('get_drug_statistics', cache_page(3600*24*365)(views.get_drug_statistics), name='get-drug-statistics'),
    path('drug/autocomplete', (selection_autocomplete), name='autocomplete'),

    #old
    path('drug/<str:drugbank_id>/', views.drug_atc_expansion, name='drug_detail'),  # still ok but template does not have much info
    path('drugbrowser', views.drugbrowser, name='drugbrowser'),  # load all the drugs - cached but still slow - might need to remove


    # Network of one drug
    path('drug_network', views.get_drug_network, name='drug-network'), #drug_network.html
    path('drug_network/<str:drug_bank_id>/general_data', views.get_drug_general_data, name='drug-network-general-data'),
    path('drug_network/<str:drug_bank_id>/drug_data', views.get_drug_data, name='drug-network-drug-data'),
    path('drug_network/<str:drug_bank_id>/interaction_data',views.get_drug_interaction_data,name='drug-network-interaction-data',),
    path('drug_network/<str:drug_bank_id>/protein_data', views.get_drug_protein_data, name='drug-network-protein-data'),
    # Network of list of drug
    path('drugs_network', views.get_drugs_network, name='drugs-network'), #drug_network.html
    path('drugs_network/general_data', views.get_drugs_general_data, name='drugs-network-general-data'),
    path('drugs_network/drug_data', views.get_drugs_data, name='drugs-network-drug-data'),
    path('drugs_network/protein_data', views.get_drugs_protein_data, name='drugs-network-protein-data'),
    path('drugs_network/interaction_data',views.get_drugs_interaction_data,name='drugs-network-interaction-data',),

    #network comparison
    path('get_data_for_comparing_network_degree_distribution/', views.get_data_for_comparing_network_degree_distribution, name='get-data-for-comparing-network-degree-distribution'),
    path('get_data_for_comparing_network_associate_distribution/', views.get_data_for_comparing_network_associate_distribution, name='get-data-for-comparing-network-associate-distribution'),
    path('get_statistics_by_atc_for_network_size_comparison/', views.get_statistics_by_atc_for_network_size_comparison, name='get-statistics-by-atc-for-network-size-comparison'),
    path('get_statistics_by_atc_for_clinical_trial_phase_comparison/', views.get_statistics_by_atc_for_clinical_trial_phase_comparison, name='get-statistics-by-atc-for-clinical-trial-phase-comparison'),
    path('get_statistics_by_atc_code_for_MOA_comparison/', views.get_statistics_by_atc_code_for_MOA_comparison, name='get-statistics-by-atc-code-for-MOA-comparison'),
    path('get_statistics_by_atc_for_measure_centralization_drug_disease/', views.get_statistics_by_atc_for_measure_centralization_drug_disease, name='get-statistics-by-atc-for-measure-centralization-drug-disease'),
    path('get_statistics_by_atc_for_measure_centralization_drug_protein/', views.get_statistics_by_atc_for_measure_centralization_drug_protein, name='get-statistics-by-atc-for-measure-centralization-drug-protein'),
    path('get_statistics_by_atc_for_detecting_community_drug_protein/', views.get_statistics_by_atc_for_detecting_community_drug_protein, name='get-statistics-by-atc-for-detecting-community-drug-protein'),
    path('get_statistics_by_atc_for_detecting_community_drug_disease/', views.get_statistics_by_atc_for_detecting_community_drug_disease, name='get-statistics-by-atc-for-detecting-community-drug-disease'),
    path('get_statistics_by_atc_for_calculating_average_path_length_drug_disease/', views.get_statistics_by_atc_for_calculating_average_path_length_drug_disease, name='get-statistics-by-atc-for-calculating-average-path-length-drug-disease'),
    path('get_statistics_by_atc_for_calculating_average_path_length_drug_protein/', views.get_statistics_by_atc_for_calculating_average_path_length_drug_protein, name='get-statistics-by-atc-for-calculating-average-path-length-drug-protein'),
    
    path('get_data_for_comparing_common_and_unique_network_element/', views.get_data_for_comparing_common_and_unique_network_element, name='get-data-for-comparing-common-and-unique-network-element'),
    path('atc_comparison_autocomplete_view/', views.atc_comparison_autocomplete_view, name='atc-comparison-autocomplete-view'),
]
