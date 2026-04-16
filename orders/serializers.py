from rest_framework import serializers
from orders.models import Cart,CartItem,Order,OrderItem,Address
from products.models import ProductVersion, Product
from users.models import Company
from orders.services import OrderService
from rest_framework.exceptions import PermissionDenied


class SimpleCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id','name','email','address','website','is_active']

class SimplePorudctSerializer(serializers.ModelSerializer):
    company = SimpleCompanySerializer()
    class Meta:
        model = Product
        fields = ['id', 'name','short_description','company','tax_rate']

class SimpleVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVersion
        fields = ['id','version','license_type','price']


class AddCartItemSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.active_objects.all(),
    )

    product_version = serializers.PrimaryKeyRelatedField(
        queryset=ProductVersion.active_objects.all(),
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_version', 'quantity']

    
    # VALIDATION (single query)
    
    def validate(self, data):
        product = data['product']
        version = data['product_version']

        if version.product_id != product.id:
            raise serializers.ValidationError(
                "Product version does not belong to this product"
            )

        return data

   
    # CREATE / UPDATE OPTIMIZED
    def save(self, **kwargs):
        cart_id = self.context.get('cart_id')
        user = self.context.get('user')

        #  Ownership check
        try:
            cart = Cart.objects.get(id=cart_id, user=user)
        except Cart.DoesNotExist:
            raise PermissionDenied("Invalid cart or you don't have permission")

        product = self.validated_data['product']
        version = self.validated_data['product_version']
        quantity = self.validated_data['quantity']



        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart_id,
            product=product,
            product_version=version,
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


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id','quantity']



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
        read_only_fields = ['user']

    def get_total_price(self, cart:Cart):
        total_price = sum([item.quantity *item.product_version.price for item in cart.items.all()])
        return total_price
        

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimplePorudctSerializer()
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','unit_price','version']\
        

class CreateOrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    cart_id = serializers.UUIDField()

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'phone_number', 'address', 'payment_method', 'cart_id',]

    def validate_cart_id(self, cart_id):
        print(" Validating cart_id:", cart_id)

        if not Cart.objects.filter(pk=cart_id).exists():
            print("Cart not found")
            raise serializers.ValidationError('No cart found with this id')

        if not CartItem.objects.filter(cart_id=cart_id).exists():
            print(" Cart is empty")
            raise serializers.ValidationError('Cart is empty')

        print(" Cart validation passed")
        return cart_id

    def create(self, validated_data):
        print("\n CREATE ORDER START")

        user_id = self.context.get('user_id')
        cart_id = validated_data.get('cart_id')
        user = self.context.get('user')
        # print(" User ID:", user_id)
        #  Ownership check
        try:
            cart = Cart.objects.get(id=cart_id, user=user)
        except Cart.DoesNotExist:
            raise PermissionDenied("Invalid cart or you don't have permission")


        try:
            order = OrderService.create_order(user_id=user_id,validated_data=validated_data)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return order
        
    
    def to_representation(self, instance):
        return OrderSerializer(instance).data 
        


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status','note','canceled_reason']
        def update(self, instance, validated_data):
            user = self.context.get('user')
            new_status = validated_data['status']

            if new_status == Order.Status.CANCELED:
                return OrderService.cancel_order(order=instance, user=user)
            
            if  not user.is_staff:
                raise serializers.ValidationError({'details': 'you are not update this order'})
            
            return super().update(instance, validated_data)
        


class OrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id','user','customer_name','phone_number','address','status','payment_method','payment_status','transaction_id','subtotal','discount','tax','total_price','note','canceled_reason','created_at','items']

        read_only_fields = ['status','payment_status']
