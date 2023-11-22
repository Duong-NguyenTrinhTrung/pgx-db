from rest_framework import serializers
from .models import VepVariant

class VepVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = VepVariant
        fields = '__all__'