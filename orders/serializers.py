from rest_framework import serializers
from orders.models import Cart,CartItem
from products.models import ProductVersion, Product
from users.models import Company

class SimpleCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id','name','email','address','website','is_active']

class SimplePorudctSerializer(serializers.ModelSerializer):
    company = SimpleCompanySerializer()
    class Meta:
        model = Product
        fields = ['id', 'name','short_description','company']

class SimpleVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVersion
        fields = ['id','version','license_type','price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimplePorudctSerializer()
    product_version = SimpleVersionSerializer()

    total_price = serializers.SerializerMethodField(method_name='get_total_price')


    class Meta:
        model = CartItem
        fields = ['id','product','product_version','quantity','total_price']


    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product_version.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    class Meta:
        model = Cart
        fields = ['id','user','items','total_price']

    def get_total_price(self, cart:Cart):
        total_price = sum([item.quantity *item.product_version.price for item in cart.items.all()])
        return total_price
        

