
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from products.models import Category,ProductImage,TechStack,Tag,Product
from products.serializers import CategorySerializer,TechStackSerializer,TagSerializer,ProductSerializer

class CategoryViewSet(ModelViewSet):
    # use active_objects manager for listing
    queryset = Category.active_objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field='slug'

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class TachStackViewSet(ModelViewSet):
    queryset = TechStack.active_objects.all()
    serializer_class = TechStackSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class TagViewSet(ModelViewSet):
    queryset = Tag.active_objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductViewSet(ModelViewSet):
    queryset = Product.active_objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field= 'slug'

    
    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.get(slug=category_slug, is_deleted=False)
        context['category_id'] = category.id
        return context
    

