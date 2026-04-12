
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.permissions import IsAuthenticated
from products.models import Category,ProductImage,TechStack,Tag,Product,ProductVersion,ProductVersionImage
from products.serializers import CategorySerializer,TechStackSerializer,TagSerializer,ProductSerializer, ProductVersionSerializer,ProductImageSerializer,ProductVersionImageSerializer, ProductDetailSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.mixins import ListModelMixin,UpdateModelMixin,RetrieveModelMixin
from rest_framework.permissions import IsAdminUser,IsAuthenticated,IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

class SoftDeleteMixin:
    """Reusable mixin for soft delete & restore"""

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            instance.soft_delete(user=user)
        else:
            instance.soft_delete()

    def destroy(self, request, *args, **kwargs):
        """Override default destroy response"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Soft deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

    

class SoftDeleteRestoreMixin:
    @action(detail=True, methods=['get','post'])
    def restore(self, request, *args, **kwargs):
        """Restore a soft-deleted object"""
        instance = self.get_object()

        if instance.is_deleted:
            instance.restore()
            return Response(
                {"status": "restored"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": "already_active"},
            status=status.HTTP_400_BAD_REQUEST
        )



class CategoryViewSet(SoftDeleteMixin, ModelViewSet):
    # use active_objects manager for listing
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name','is_active']
    lookup_field='slug'

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        user = self.request.user

        if user.role =='is_staff' or user.role=='is_superuser':
            return Category.objects.all()
        
        return Category.active_objects.all()


class RestoreCategoryViewSet(SoftDeleteRestoreMixin,ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Category.deleted_objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminUser]

    
class TachStackViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = TechStack.active_objects.all()
    serializer_class = TechStackSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RestoreTeckStackViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = TechStack.deleted_objects.all()
    serializer_class = TechStackSerializer
    permission_classes = [IsAdminUser]

    

    
class TagViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = Tag.active_objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RestoreTagViewSet(SoftDeleteRestoreMixin,ModelViewSet):
    queryset = Tag.deleted_objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    

class ProductViewSet(ListModelMixin,GenericViewSet):
    """product list only"""
    queryset = Product.active_objects.select_related('category').all()
    serializer_class = ProductSerializer

    

class ProductDetailViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = Product.active_objects.select_related('category').prefetch_related('images','versions','tech_stack','tags').all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company','name','category','tech_stack','versions']
    lookup_field= 'slug'

    
    def get_serializer_context(self):
        
        # Pass request for created_by
        context = super().get_serializer_context()
        
        if getattr(self, 'swagger_fake_view', False):
            return context
        
        context['request'] = self.request
        category_slug = self.kwargs.get('category_slug')
        category = Category.objects.get(slug=category_slug)
        context['category_id'] = category.id
        return context

class RestoreProductViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = Product.deleted_objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
  
    
class ProductVersionViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = ProductVersion.active_objects.all()
    serializer_class = ProductVersionSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access
    lookup_field='slug'

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context
        
        context['request'] = self.request  # Add request to context
        product_slug = self.kwargs.get('product_slug')
        product = Product.active_objects.get(slug=product_slug)
        context['product_id']=product.id
        return context
    
class RestoreProductVersionViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = ProductVersion.deleted_objects.all()
    serializer_class = ProductVersionSerializer
    permission_classes = [IsAdminUser]
    

class ProductImageViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = ProductImage.active_objects.all()
    serializer_class = ProductImageSerializer

    
    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context
        
        context['request'] = self.request  # Add request to context
        product_slug = self.kwargs.get('product_slug')
        product = Product.active_objects.get(slug=product_slug)
        context['product_id']=product.id
        return context
    

class RestoreProductImageViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = ProductImage.deleted_objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]


class ProductVersionImageViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = ProductVersionImage.active_objects.all()
    serializer_class = ProductVersionImageSerializer

    
    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context
        
        context['request'] = self.request  # Add request to context
        version_slug = self.kwargs.get('version_slug')
        version = ProductVersion.active_objects.get(slug=version_slug)
        context['version_id']=version.id
        return context

class RestoreProductVersionImageViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    queryset = ProductVersionImage.deleted_objects.all()
    serializer_class = ProductVersionImageSerializer
    permission_classes = [IsAdminUser]  