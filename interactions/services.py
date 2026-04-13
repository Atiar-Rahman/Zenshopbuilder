from interactions.models import ProductView,ProductLike, Wishlist
from products.models import Product
from django.db.models import F
from django.db.models.functions import Greatest


class ProductService:
    @staticmethod
    def add_view(product,user):
        obj,created = ProductView.objects.get_or_create(
            product=product,
            user=user
        )
        if created:
            Product.objects.filter(id=product.id).update(
                total_views = F('total_views')+1
            )
    

    @staticmethod
    def toggle_like(product, user):
        like, created = ProductLike.objects.get_or_create(
            product  = product,
            user = user
        )

        if not created:
            like.delete()
            Product.objects.filter(id=product.id).update(
                total_likes = Greatest(F('total_likes') - 1,0)
            )
        else:
            Product.objects.filter(id=product.id).update(
                total_likes = F('total_likes') + 1
            )


    @staticmethod
    def toggle_wishlist(product, user):
        item, created = Wishlist.objects.get_or_create(
            product = product,
            user = user
        )

        if not created:
            item.delete()

            Product.objects.filter(id=product.id).update(
                total_wishlist = Greatest(F('total_wishlist')-1,0)
            )
        else:
            Product.objects.filter(id=product.id).update(
                total_wishlist = F('total_wishlist') + 1
            )
        