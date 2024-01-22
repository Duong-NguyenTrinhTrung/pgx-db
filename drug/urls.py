from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import SelectionAutocomplete, DrugStatistics
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
    get_statistics_by_atc_for_calculating_average_path_length_drug_protein
)

urlpatterns = [
    path('search_drugs', views.search_drugs, name='search_drugs'),
    path('atc-lookup', cache_page(3600*24*7)(views.atc_lookup), name='atc-lookup'),
    path('atc-anatomical-groups', views.AtcAnatomicalGroupListView.as_view(), name='atc-anatomical-groups'),
    path('atc_search_view', cache_page(3600*24*7)(views.atc_search_view), name='atc_search_view'),

    path('atc-detail-view/', views.atc_detail_view, name='atc-detail-view'),
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
    path('get-atc-sub-levels/', views.get_atc_sub_levels, name='get-atc-sub-levels'),
    path('drugbrowser', views.drugbrowser, name='drugbrowser'),  # load all the drugs - cached but still slow - might need to remove
    # path('drugstatistic', (DrugStatistics.as_view()), name='drugstatistic'),  # okie but with dummy data
    path('drugstatistic', (views.DrugStatistics), name='drugstatistic'),  # okie but with dummy data
    path('drug/autocomplete', (SelectionAutocomplete), name='autocomplete'),
    path('drug/<str:drugbank_id>/', views.drug_atc_expansion, name='drug_detail'),  # still ok but template does not have much info


    # Network of one drug
    path('drug_network', views.get_drug_network, name='drug_network'), #drug_network.html
    path('drug_network/<str:drug_bank_id>/general_data', views.get_drug_general_data, name='drug_network_general_data'),
    path('drug_network/<str:drug_bank_id>/drug_data', views.get_drug_data, name='drug_network_drug_data'),
    path('drug_network/<str:drug_bank_id>/interaction_data',views.get_drug_interaction_data,name='drug_network_interaction_data',),
    path('drug_network/<str:drug_bank_id>/protein_data', views.get_drug_protein_data, name='drug_network_protein_data'),
    # Network of list of drug
    path('drugs-network', views.get_drugs_network, name='drugs_network'), #drug_network.html
    path('drugs-network/general-data', views.get_drugs_general_data, name='drugs_network_general_data'),
    path('drugs-network/drug-data', views.get_drugs_data, name='drugs_network_drug_data'),
    path('drugs-network/protein-data', views.get_drugs_protein_data, name='drugs_network_protein_data'),
    path('drugs-network/interaction-data',views.get_drugs_interaction_data,name='drugs_network_interaction_data',),

    #network comparison
    path('get_data_for_comparing_network_degree_distribution/', views.get_data_for_comparing_network_degree_distribution, name='get_data_for_comparing_network_degree_distribution'),
    path('get_data_for_comparing_network_associate_distribution/', views.get_data_for_comparing_network_associate_distribution, name='get_data_for_comparing_network_associate_distribution'),
    path('get_statistics_by_atc_for_network_size_comparison/', views.get_statistics_by_atc_for_network_size_comparison, name='get_statistics_by_atc_for_network_size_comparison'),
    path('get_statistics_by_atc_for_clinical_trial_phase_comparison/', views.get_statistics_by_atc_for_clinical_trial_phase_comparison, name='get_statistics_by_atc_for_clinical_trial_phase_comparison'),
    path('get_statistics_by_atc_code_for_MOA_comparison/', views.get_statistics_by_atc_code_for_MOA_comparison, name='get_statistics_by_atc_code_for_MOA_comparison'),
    path('get_statistics_by_atc_for_measure_centralization_drug_disease/', views.get_statistics_by_atc_for_measure_centralization_drug_disease, name='get_statistics_by_atc_for_measure_centralization_drug_disease'),
    path('get_statistics_by_atc_for_measure_centralization_drug_protein/', views.get_statistics_by_atc_for_measure_centralization_drug_protein, name='get_statistics_by_atc_for_measure_centralization_drug_protein'),
    path('get_statistics_by_atc_for_detecting_community_drug_protein/', views.get_statistics_by_atc_for_detecting_community_drug_protein, name='get_statistics_by_atc_for_detecting_community_drug_protein'),
    path('get_statistics_by_atc_for_detecting_community_drug_disease/', views.get_statistics_by_atc_for_detecting_community_drug_disease, name='get_statistics_by_atc_for_detecting_community_drug_disease'),
    path('get_statistics_by_atc_for_calculating_average_path_length_drug_disease/', views.get_statistics_by_atc_for_calculating_average_path_length_drug_disease, name='get_statistics_by_atc_for_calculating_average_path_length_drug_disease'),
    path('get_statistics_by_atc_for_calculating_average_path_length_drug_protein/', views.get_statistics_by_atc_for_calculating_average_path_length_drug_protein, name='get_statistics_by_atc_for_calculating_average_path_length_drug_protein'),
    
    path('get_data_for_comparing_common_and_unique_network_element/', views.get_data_for_comparing_common_and_unique_network_element, name='get_data_for_comparing_common_and_unique_network_element'),
]
