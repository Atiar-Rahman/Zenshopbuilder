from django.shortcuts import render

# Create your views here.
from interactions.models import RecentlyViewed
from interactions.serializers import HistorySerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
class HistoryViewSet(ModelViewSet):
    """History create only retrieve product viewset autocreated history get and delete authenticated permission"""
    serializer_class = HistorySerializer
    permission_classes= [IsAuthenticated]
    http_method_names = ['get','delete']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return RecentlyViewed.objects.none()
        return RecentlyViewed.objects.filter(user=user)
    