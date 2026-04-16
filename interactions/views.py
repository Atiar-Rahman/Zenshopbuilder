from django.shortcuts import render

# Create your views here.
from interactions.models import RecentlyViewed
from interactions.serializers import HistorySerializer
from rest_framework.viewsets import ModelViewSet

class HistoryViewSet(ModelViewSet):
    serializer_class = HistorySerializer

    def get_queryset(self):
        return RecentlyViewed.objects.filter(user = self.request.user)
    