from rest_framework import serializers
from orders.models import Cart,CartItem,Order,OrderItem,Address
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
        fields = ['id', 'name','short_description','company','tax_rate']

class SimpleVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVersion
        fields = ['id','version','license_type','price']


class AddCartItemSerialzer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )

    product_version = serializers.PrimaryKeyRelatedField(
        queryset=ProductVersion.objects.all(),
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
        # print(" User ID:", user_id)

        cart_id = validated_data.pop('cart_id')
        address_data = validated_data.pop('address')

        # print(" Cart ID:", cart_id)
        # print("Address Data:", address_data)

        # get cart
        cart = Cart.objects.get(pk=cart_id)
        # print("Cart fetched:", cart)

        # get cart items
        cart_items = cart.items.select_related('product', 'product_version').all()
        print(f" Cart Items Count: {cart_items.count()}")

        # create address
        address = Address.objects.create(**address_data)
        # print(" Address created:", address)
        
        grand_total=0
        subtotal = 0
        tax_total = 0
        discount_total=0
        order_items = []
        

        for item in cart_items:
            # print(item)
            product = item.product
            version = item.product_version
            unit_price = version.price
            discount_price = version.discount_price
            quantity = item.quantity
            license_type=version.license_type

            tax_rate = product.tax_rate or 0
            line_total = unit_price*quantity
            tax = line_total * tax_rate/100
            
            discount = discount_price*quantity
            total_price = line_total-discount+tax
            subtotal+=line_total
            tax_total +=tax
            discount_total +=discount
            grand_total += total_price

            order_items.append({
                'product':product,
                'product_version':version,
                'product_name':product.name,
                'version':version.version,
                'unit_price': unit_price,
                'quantity': quantity,
                'license_type':license_type,
                'tax':tax,
                'total_price':total_price
            })

        print(order_items)

        #order create
        order = Order.objects.create(
            user_id = user_id,
            customer_name = validated_data.get('customer_name'),
            phone_number = validated_data.get('phone_number'),
            address = address,
            subtotal = subtotal,
            tax = tax_total,
            discount = discount_total,
            total_price=grand_total,
            payment_method= validated_data.get('payment_method')
        )



        
        print(" Order created:", order.id)


        #bulk create 
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item['product'],
                product_version = item['product_version'],
                product_name = item['product_name'],
                version = item['version'],
                license_type = item['license_type'],
                unit_price = item['unit_price'],
                quantity = item['quantity'],
                tax = item['tax'],
                total_price = item['total_price']
            )
            for item in order_items
        ])

        cart.delete()


        return order
    
    def to_representation(self, instance):
        return OrderSerializer(instance).data 
        



class OrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id','user','customer_name','phone_number','address','status','payment_method','payment_status','transaction_id','subtotal','discount','tax','total_price','note','canceled_reason','created_at','items']

        read_only_fields = ['status','payment_status']
