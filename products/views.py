
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.permissions import IsAuthenticated
from products.models import Category,ProductImage,TechStack,Tag,Product,ProductVersion,ProductVersionImage
from products.serializers import CategorySerializer,TechStackSerializer,TagSerializer,ProductSerializer, ProductVersionSerializer,ProductImageSerializer,ProductVersionImageSerializer, ProductDetailSerializer,ProductWriteSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.mixins import ListModelMixin,UpdateModelMixin,RetrieveModelMixin
from rest_framework.permissions import IsAdminUser,IsAuthenticated,AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from products.filters import ProductFilter
from django.db.models import Min, Max
from products.paginations import CustomPagination
from interactions.services import ProductService
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

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
    
    @action(detail=True, methods=['get','delete'])
    def hard_delete(self, request, slug=None):
        instance = self.get_object()

        if instance.products.exists():
            return Response(
                {"error": "Cannot delete category with products"},
                status=400
            )
        instance.delete()
        return Response({"message": "Permanently deleted"})


class CategoryViewSet(SoftDeleteMixin, ModelViewSet):
    # use active_objects manager for listing
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['name','is_active']
    search_fields = ['name']
    ordering_fields = ['created_at','is_active']
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
    http_method_names = ['get','delete']
    queryset = Category.deleted_objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminUser]

    
class TachStackViewSet(SoftDeleteMixin, ModelViewSet):
    queryset = TechStack.active_objects.all()
    serializer_class = TechStackSerializer
    filter_backends = [SearchFilter,OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RestoreTeckStackViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    """TachStack Restore must be AdminUser"""
    http_method_names=['get']
    queryset = TechStack.deleted_objects.all()
    serializer_class = TechStackSerializer
    permission_classes = [IsAdminUser]

    

    
class TagViewSet(SoftDeleteMixin, ModelViewSet):
    """Tag crud operation by authenticated user"""
    queryset = Tag.active_objects.all()
    serializer_class = TagSerializer
    filter_backends = [SearchFilter,OrderingFilter]
    
    search_fields = ['name']
    ordering_fields = ['created_at']
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_context(self):
        # Pass request for created_by
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class RestoreTagViewSet(SoftDeleteRestoreMixin,ModelViewSet):
    """Restore deleted tag only admin"""
    http_method_names=['get']
    queryset = Tag.deleted_objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    

class ProductViewSet(ListModelMixin,RetrieveModelMixin, GenericViewSet):
    queryset = Product.active_objects.select_related('category').annotate(
        min_price=Min('versions__price'),
        max_price =Max('versions__price')
    )
    pagination_class = CustomPagination
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_class = ProductFilter
    search_fields = ['name', 'tech_stack']

    ordering_fields = ['created_at', 'total_views', 'min_price','max_price']

    #all service product related

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()

        if request.user.is_authenticated:
            ProductService.add_view(product, request.user)

        return super().retrieve(request, *args, **kwargs)
    

    @action(detail=True, methods=['get','post'])
    def toggle_like(self, request, pk=None):
        product = self.get_object()

        ProductService.toggle_like(product, request.user)

        return Response(
            {"message": "Like toggled"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get','post'])
    def toggle_wishlist(self, request, pk=None):
        product = self.get_object()

        ProductService.toggle_wishlist(product, request.user)

        return Response(
            {"message": "Wishlist toggled"},
            status=status.HTTP_200_OK
        )
    

class ProductDetailViewSet(SoftDeleteMixin, ModelViewSet):
    lookup_field = 'slug'

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        'company': ['exact'],
        'category': ['exact'],
        'name': ['icontains'],
    }

    search_fields = ['name', 'tech_stack__name']
    ordering_fields = ['created_at', 'total_views']

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        elif self.action == 'list':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = Product.objects.all()

        if self.action in ['list', 'retrieve']:
            queryset = Product.active_objects

        return queryset.select_related('category').prefetch_related(
            'images', 'versions', 'tech_stack', 'tags'
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        return ProductDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, 'swagger_fake_view', False):
            return context

        if 'category_slug' in self.kwargs:
            context['category_id'] = Category.objects.filter(
                slug=self.kwargs['category_slug']
            ).values_list('id', flat=True).first()

        return context

class RestoreProductViewSet(SoftDeleteRestoreMixin, ModelViewSet):
    """Restore only adminuser"""
    http_method_names = ['get']
    queryset = Product.deleted_objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
  
    
class ProductVersionViewSet(SoftDeleteMixin, ModelViewSet):
    """Product Version show only authenticated user others operation only adminuser"""
    queryset = ProductVersion.active_objects.all()
    serializer_class = ProductVersionSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field='slug'

    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]

    filterset_fields = ['version','price']


    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

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
    """Restore product version only admin user"""
    http_method_names = ['get']
    queryset = ProductVersion.deleted_objects.all()
    serializer_class = ProductVersionSerializer
    permission_classes = [IsAdminUser]
    

class ProductImageViewSet(SoftDeleteMixin, ModelViewSet):
    """Product Image get only authenticated user others operation adminuser"""
    queryset = ProductImage.active_objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
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
    """RestoreProduct image only admin user"""
    http_method_names = ['get']
    queryset = ProductImage.deleted_objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]


class ProductVersionImageViewSet(SoftDeleteMixin, ModelViewSet):
    """Product Image get only authenticated user and other operation adminuser"""
    queryset = ProductVersionImage.active_objects.all()
    serializer_class = ProductVersionImageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    
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
    """Restore ProductVersion Image only Admin user"""
    http_method_names = ['get']
    queryset = ProductVersionImage.deleted_objects.all()
    serializer_class = ProductVersionImageSerializer
    permission_classes = [IsAdminUser]  

