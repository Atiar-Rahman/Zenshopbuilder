from django.db import models
from products.models import Product


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='views')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email 
    
    class Meta:
        unique_together = ('product','user')


class ProductLike(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email 
    
    class Meta:
        unique_together = ('product','user')

class Wishlist(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email 
    
    class Meta:
        unique_together = ('product','user')


class RecentlyViewed(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=1)
    last_viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-viewed_at']