from django.urls import path
from django.views.decorators.cache import cache_page
from .views import InteractionBrowser


urlpatterns = [
    path('interaction', (InteractionBrowser.as_view()), name='interaction_browser'),
]
