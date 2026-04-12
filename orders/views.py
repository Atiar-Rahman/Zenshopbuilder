from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from orders.models import Cart, CartItem
from orders.serializers import CartSerializer, CartItemSerializer, AddCartItemSerialzer, UpdateCartItemSerializer
from rest_framework.permissions import IsAuthenticated


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


    
class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

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
        return CartItem.objects.filter(cart_id=self.kwargs.get('cart_pk'))