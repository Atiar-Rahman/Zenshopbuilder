from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from orders.models import Cart, CartItem,Order,OrderItem
from orders.serializers import CartSerializer, CartItemSerializer, AddCartItemSerialzer, UpdateCartItemSerializer, OrderSerializer,CreateOrderSerializer,UpdateOrderSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items').filter(user=self.request.user)


    
class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product','product_version']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerialzer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['cart_id'] = self.kwargs.get('cart_pk')

        return context

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs.get('cart_pk'))
    



# order viewset
class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer_name','phone_number','status','payment_status','transaction_id']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options', 'trace']
    def get_serializer_class(self):

        if self.request.method=='POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH' :
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        
        return {'user_id':self.request.user.id,'user':self.request.user}

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
    
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items').all()
        return Order.objects.filter(user = self.request.user)
    