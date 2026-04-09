from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from products.models import Category
from products.serializers import CategorySerializer

class CategoryViewSet(ModelViewSet):
    # use active_objects manager for listing
    queryset = Category.active_objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context