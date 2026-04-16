from interactions.models import ProductView,ProductLike, Wishlist,RecentlyViewed
from products.models import Product
from django.db.models import F
from django.db.models.functions import Greatest


class ProductService:
    @staticmethod
    def track_view(product,user):
        obj,created = ProductView.objects.get_or_create(
            product=product,
            user=user
        )

        if created:
            Product.objects.filter(id=product.id).update(
                total_views = F('total_views')+1
            )
        RecentlyViewed.objects.update_or_create(
            user=user,
            product=product
        )

        obj, created = RecentlyViewed.objects.get_or_create(
             user=user,
             product=product
             )

        if not created:
            obj.view_count += 1
            obj.save(update_fields=["view_count", "last_viewed_at"])

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
        