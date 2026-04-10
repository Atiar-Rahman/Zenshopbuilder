from core.models import SoftDeleteModel
from django.contrib.auth import get_user_model
from django.db import models
from products.models import Product,ProductVersion

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
    


class Order(SoftDeleteModel):

    class Status(models.TextChoices):
        NOT_PAID = "NOT_PAID", "Not Paid"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELED = "CANCELED", "Canceled"
        REFUNDED = "REFUNDED", "Refunded"


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    # Order Lifecycle
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_PAID,
        db_index=True
    )

    #  Payment Info
    payment_method = models.CharField(max_length=50)  # Stripe / SSLCommerz
    payment_status = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)

    #  Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    #  Extra
    note = models.TextField(blank=True, null=True)
    canceled_reason = models.TextField(blank=True, null=True)

   
    #  calculate total (optional helper)
    def calculate_total(self):
        return sum(item.total_price for item in self.items.all())

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

    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    

    # auto calculation
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} ({self.license_type}) x {self.quantity}"