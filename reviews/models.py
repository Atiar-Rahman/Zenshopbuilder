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

    def clean(self):
        # Ensure rating between 0-5
        if not (0 <= self.rating <= 5):
            raise ValidationError("Rating must be between 0 and 5")

    def __str__(self):
        return f"{self.title} - {self.product.name}"

    # Optional: auto update Product rating & total_reviews
    def save(self, *args, **kwargs):
        self.full_clean()  # call clean()
        super().save(*args, **kwargs)
        # Update product rating after saving
        self.product.update_rating()
