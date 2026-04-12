from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from orders.models import Cart, CartItem
from orders.serializers import CartSerializer, CartItemSerializer
from rest_framework.permissions import IsAuthenticated


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset= Cart.objects.all()
    serializer_class = CartSerializer

    
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(id=self.kwargs.get('cart_pk'))