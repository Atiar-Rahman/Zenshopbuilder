from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from orders.models import Cart
from orders.serializers import CartSerializer

class CartViewSet(CreateModelMixin,RetrieveModelMixin, GenericViewSet):
    queryset= Cart.objects.all()
    serializer_class = CartSerializer

    