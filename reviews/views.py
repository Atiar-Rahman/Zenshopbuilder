from rest_framework.viewsets import ModelViewSet
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from products.models import Product
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated

class ReviewViewSet(ModelViewSet):
    """Review delete only admin user other operation create, get, patch, put only authenticated user"""
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(),IsAdminUser()]
        
        return [IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context
        
        product = get_object_or_404(
            Product,
            slug=self.kwargs.get('product_slug')
        )

        context['product'] = product
        context['user'] = self.request.user
        return context
        
    
    