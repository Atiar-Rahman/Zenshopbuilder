from django.db import models
from django.core.exceptions import ValidationError
from core.models import SoftDeleteModel
from products.models import Product  # Assuming your Product model is here

class Review(SoftDeleteModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=200)
    rating = models.FloatField()
    comment = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product_review'
            )
        ]
    def __str__(self):
        return f"{self.title} - {self.product.name}"


