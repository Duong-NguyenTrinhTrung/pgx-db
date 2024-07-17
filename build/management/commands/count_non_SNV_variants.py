# your_app/management/commands/count_variants.py

from django.core.management.base import BaseCommand
from variant.models import VepVariant

class Command(BaseCommand):
    help = 'Counts the rows in VepVariant where the last part of Variant_marker contains more than 3 characters'

    def handle(self, *args, **kwargs):
        all_variants = VepVariant.objects.all()
        count = 0

        for variant in all_variants:
            parts = variant.Variant_marker.VariantMarker.split('_')
            if len(parts[-1]) > 3:
                print(variant.Variant_marker.VariantMarker)
                count += 1

        self.stdout.write(f'The number of rows where the last part of Variant_marker contains more than 3 characters: {count}')
