from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Image

class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def create(self, validated_data):
        image = Image.objects.create(
            image=validated_data['image']
        )
        return image