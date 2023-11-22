import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

# First, import the necessary models and functions
from protein.models import Protein
from variant.models import Variant, VepVariant

uniprotID = "P07477"
print("TEST")