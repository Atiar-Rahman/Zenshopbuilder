from orders.models import Cart,Address,OrderItem,Order
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from decimal import Decimal

class OrderService:
    @staticmethod
    def create_order(user_id, validated_data):
        with transaction.atomic():

            cart_id = validated_data.pop('cart_id')
            address_data = validated_data.pop('address')

            # ownership check
            cart = Cart.objects.get(pk=cart_id, user_id=user_id)

            cart_items = cart.items.select_related('product', 'product_version')

            if not cart_items.exists():
                raise ValidationError("Cart is empty")

            # address create (optional: get_or_create)
            address = Address.objects.create(**address_data)

            subtotal = Decimal('0')
            tax_total = Decimal('0')
            discount_total = Decimal('0')
            grand_total = Decimal('0')

            order_items = []

            for item in cart_items:
                product = item.product
                version = item.product_version

                #  MUST: cart snapshot price
                unit_price = item.unit_price

                quantity = item.quantity
                tax_rate = Decimal(product.tax_rate or 0)
                discount_percent = Decimal(version.discount_price or 0)

                line_total = unit_price * quantity

                #  discount (percentage ভিত্তিক)
                discount = (line_total * discount_percent) / Decimal(100)

                taxable_amount = line_total - discount

                tax = (taxable_amount * tax_rate) / Decimal(100)

                total_price = taxable_amount + tax

                # totals
                subtotal += line_total
                discount_total += discount
                tax_total += tax
                grand_total += total_price

                order_items.append({
                    'product': product,
                    'product_version': version,
                    'product_name': product.name,
                    'version': version.version,
                    'license_type': version.license_type,
                    'unit_price': unit_price,
                    'quantity': quantity,
                    'discount': discount,
                    'tax': tax,
                    'total_price': total_price
                })

            #  order create
            order = Order.objects.create(
                user_id=user_id,
                customer_name=validated_data.get('customer_name'),
                phone_number=validated_data.get('phone_number'),
                address=address,
                subtotal=subtotal,
                discount=discount_total,
                tax=tax_total,
                total_price=grand_total,
                payment_method=validated_data.get('payment_method'),
                payment_status=Order.PaymentStatus.PENDING
            )

            # bulk create
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item['product'],
                    product_version=item['product_version'],
                    product_name=item['product_name'],
                    version=item['version'],
                    license_type=item['license_type'],
                    unit_price=item['unit_price'],
                    quantity=item['quantity'],
                    discount=item['discount'],   #  added
                    tax=item['tax'],
                    total_price=item['total_price']
                )
                for item in order_items
            ])

            # clear cart
            cart.delete()

            return order
        

    @staticmethod
    def cancel_order(order, user):

        #  ownership / admin
        if not user.is_staff and order.user != user:
            raise PermissionDenied({'detail': 'You can only cancel your own order'})

        #  already canceled
        if order.status == Order.Status.CANCELED:
            raise ValidationError({'detail': 'Order already canceled'})

        #  completed order
        if order.status == Order.Status.COMPLETED:
            raise ValidationError({'detail': 'Completed order cannot be canceled'})

        #  paid order → optional refund logic
        if order.payment_status == Order.PaymentStatus.PAID:
            # এখানে refund system integrate করতে পারো
            order.payment_status = Order.PaymentStatus.REFUNDED

        order.status = Order.Status.CANCELED
        order.save()

        return order
    