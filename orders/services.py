from orders.models import Cart,Address,OrderItem,Order
from django.db import transaction


class OrderService:
    @staticmethod
    def create_order(user_id,validated_data):
        with transaction.atomic():
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