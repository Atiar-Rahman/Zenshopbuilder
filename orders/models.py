from core.models import SoftDeleteModel
from django.contrib.auth import get_user_model
from django.db import models
from products.models import Product,ProductVersion
from django.core.exceptions import ValidationError
import phonenumbers
from phonenumbers import NumberParseException

User = get_user_model()

class Cart(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return self.user.email


class CartItem(SoftDeleteModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    product_version = models.ForeignKey(
        ProductVersion,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    quantity = models.PositiveIntegerField(default=1)

    

    

    class Meta:
        unique_together = [['cart', 'product_version']]


    def __str__(self):
        return f"{self.product.name} ({self.product_version.license_type})"
    

# --- Global phone vlidator---

def validate_phone_number(value):
    try:
        number = phonenumbers.parse(value, None)  # None = any country

        if not phonenumbers.is_valid_number(number):
            raise ValidationError("Enter a valid phone number")

    except NumberParseException:
        raise ValidationError("Enter a valid phone number")


class Address(models.Model):
    street_address = models.TextField() # main text address(road, area)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=100, default='Bangladesh')

    def __str__(self):
        return f'{self.street_address}, {self.city},{self.postal_code}, {self.country}'






class Order(SoftDeleteModel):

    class Status(models.TextChoices):
        NOT_PAID = "NOT_PAID", "Not Paid"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELED = "CANCELED", "Canceled"
        REFUNDED = "REFUNDED", "Refunded"

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    class PaymentMethod(models.TextChoices):
        STRIPE = "STRIPE", "Stripe"
        SSLCOMMERZ = "SSLCOMMERZ", "SSLCommerz"
        CASH = "CASH", "Cash"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    customer_name = models.CharField(max_length=100, default='unknown')

    phone_number = models.CharField(
        validators=[validate_phone_number],
        max_length=20
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_PAID,
        db_index=True
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True
    )

    transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )   

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    note = models.TextField(blank=True, null=True)
    canceled_reason = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Order {self.id} - {self.status}"

class OrderItem(SoftDeleteModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    #  Reference (optional but useful)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products'
    )

    product_version = models.ForeignKey(
        ProductVersion,
        on_delete=models.CASCADE,
        related_name='order_versions'
    )

    #  SNAPSHOT (MOST IMPORTANT)
    product_name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    license_type = models.CharField(max_length=20)

    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    tax = models.DecimalField(max_digits=12, decimal_places=2,default=0)

    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    

    def __str__(self):
        return f"{self.product_name} ({self.license_type}) x {self.quantity}"