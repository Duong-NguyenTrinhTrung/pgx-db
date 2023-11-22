import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

from interaction.models import Interaction
from django.db.models import Count

# Count the number of each interaction_type and return the result as a dictionary
interaction_count = Interaction.objects.values('interaction_type').annotate(count=Count('interaction_type'))

# Print the result
for interaction in interaction_count:
    print(interaction['interaction_type'], interaction['count'])
