from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from orders.models import Cart, CartItem,Order,OrderItem
from orders.serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from products.paginations import CustomPagination


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    """Cart created only authenticated user"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items').filter(user=self.request.user)


    
class CartItemViewSet(ModelViewSet):
    """CartItem add, delete, update, partialup only authenticated user from owner cart """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product','product_version']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['cart_id'] = self.kwargs.get('cart_pk')
        context['user'] = self.request.user

        return context

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter( cart_id=self.kwargs.get('cart_pk'),cart__user = self.request.user)
    



# order viewset
class OrderViewSet(ModelViewSet):
    """Order only cartItem must be owner cart only authenticated user"""
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['status', 'payment_status']
    search_fields = ['user__email']
    ordering_fields = ['created_at', 'total_price']

    pagination_class = CustomPagination

    http_method_names = ['get', 'post', 'patch', 'delete']
    def get_serializer_class(self):

        if self.request.method=='POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH' :
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(),IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        
        return {'user_id':self.request.user.id,'user':self.request.user}

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
    
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items').all()
        return Order.objects.filter(user = self.request.user)
    