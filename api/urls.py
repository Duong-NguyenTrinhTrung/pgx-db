from django.urls import path
from gene.views import GeneDetailApiView
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


app_name = 'api'

urlpatterns = (
    path('gene/<slug:gene_id>/', GeneDetailApiView.as_view(), name='gene'),
)
### API
