import django_filters

from drug.models import AtcAnatomicalGroup


class AtcAnatomicalGroupFilter(django_filters.FilterSet):
    class Meta:
        model = AtcAnatomicalGroup
        fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains'],
        }
