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


class AddCartItemSerialzer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product_id'
    )

    product_version = serializers.PrimaryKeyRelatedField(
        queryset=ProductVersion.objects.all(),
        source='product_version_id'
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_version', 'quantity']

    
    # VALIDATION (single query)
    
    def validate(self, data):
        product = data['product_id']
        version = data['product_version_id']

        if version.product_id != product.id:
            raise serializers.ValidationError(
                "Product version does not belong to this product"
            )

        return data

   
    # CREATE / UPDATE OPTIMIZED
    def save(self, **kwargs):
        cart_id = self.context.get('cart_id')

        product = self.validated_data['product_id']
        version = self.validated_data['product_version_id']
        quantity = self.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart_id,
            product_id=product,
            product_version_id=version,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        self.instance = cart_item
        return self.instance


    # Quantity validation
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Quantity must be greater than 0'
            )
        return value



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
        

