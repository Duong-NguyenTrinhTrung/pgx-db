from django.urls import path

from .views import (
    get_genebass_tables,
    get_variant_vep_scores_and_plot,
)

app_name = 'variant'

urlpatterns = [
    path('genebass_variants/', get_genebass_tables, name='get-genebass-tables'),
    path('plot-variants/', get_variant_vep_scores_and_plot, name='get-plots'),
    ]
