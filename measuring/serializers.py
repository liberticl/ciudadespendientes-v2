from rest_framework import serializers
from .models import TrafficCount

class TrafficCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficCount
        fields = (
            'timestamp', 'latitude', 'longitude',
            'car_count', 'person_count', 'bicycle_count',
            'motorcycle_count', 'truck_count', 'bus_count'
        )

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        device = self.context['request'].user

        return TrafficCount.objects.create(
            location=f'POINT({longitude} {latitude})',
            device=device,
            **validated_data
        )