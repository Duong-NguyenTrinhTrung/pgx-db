# from django.conf.urls import url
from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from .views import ProteinBrowser
from . import views
from django.conf.urls.static import static
import os
from conf import settings


urlpatterns = [
    #  url(r'^browser$', cache_page(3600*24*7)(views.LigandBrowser.as_view()), name='ligand_browser'),
    path('protein',
         (ProteinBrowser.as_view()), name='protein_browser'),
    re_path(r'^protein/(?P<slug>[\w-]+)/$', views.get_protein_details, name='detail'),
    path('protein_view_ex', views.protein_view_ex, name='protein-view'),
]

# Define a URL route for serving data files
"""
- static() is a function provided by Django that generates a URL pattern for serving static files. In this case, we are using it to serve our data files instead of static files.
The first argument to static() is the URL prefix for the files. In this case, we are using the URL /data/. When a request is made to this URL, Django will try to find the requested file in the directory specified by the document_root argument.
- The document_root argument is the directory where our data files are located. We are using the DATA_DIR setting that we defined earlier to specify this directory.
- Finally, we are adding the generated URL pattern to the urlpatterns list using the += operator. This makes our data files accessible to the Django application, and allows us to use the /data/ URL prefix in our JavaScript code to access the files.
"""
urlpatterns += static('/data/', document_root=settings.DATA_DIR)