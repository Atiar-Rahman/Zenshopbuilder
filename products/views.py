
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from products.models import Category,ProductImage,TechStack,Tag,Product,ProductVersion,ProductVersionImage
from products.serializers import CategorySerializer,TechStackSerializer,TagSerializer,ProductSerializer, ProductVersionSerializer,ProductImageSerializer,ProductVersionImageSerializer
from rest_framework.response import Response
class SoftDeleteRestoreMixin:
    """Mixin to handle soft delete and restore logic for viewsets."""
    
    def restore(self, request, *args, **kwargs):
        """Restore a soft-deleted object."""
        instance = self.get_object()
        if instance.is_deleted:
            instance.restore()  # Call restore method of the model
            return Response({"status": "restored"})
        return Response({"status": "already_active"})

    def perform_destroy(self, instance):
        """Perform soft delete."""
        instance.soft_delete(user=self.request.user)  # Optionally, pass the u



class CategoryViewSet(SoftDeleteRestoreMixin, ModelViewSet):
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
    
class TachStackViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = TechStack.active_objects.all()
    serializer_class = TechStackSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class TagViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = Tag.active_objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = Product.active_objects.select_related('category').prefetch_related('images','versions','tech_stack','tags').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    lookup_field= 'slug'

    
    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.get(slug=category_slug)
        context['category_id'] = category.id
        return context
    

class ProductVersionViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = ProductVersion.active_objects.all()
    serializer_class = ProductVersionSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    lookup_field='slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # Add request to context
        product_slug = self.kwargs.get('product_slug')
        product = Product.active_objects.get(slug=product_slug)
        context['product_id']=product.id
        return context

    

class ProductImageViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = ProductImage.active_objects.all()
    serializer_class = ProductImageSerializer

    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # Add request to context
        product_slug = self.kwargs.get('product_slug')
        product = Product.active_objects.get(slug=product_slug)
        context['product_id']=product.id
        return context

class ProductVersionImageViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = ProductVersionImage.active_objects.all()
    serializer_class = ProductVersionImageSerializer

    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # Add request to context
        version_slug = self.kwargs.get('version_slug')
        version = ProductVersion.active_objects.get(slug=version_slug)
        context['version_id']=version.id
        return context
    