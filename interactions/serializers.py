from interactions.models import RecentlyViewed
from rest_framework import serializers
from products.serializers import ProductSerializer

class HistorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ['id','user','product','viewed_at','view_count','last_viewed_at']

