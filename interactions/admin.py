from django.contrib import admin
from interactions.models import ProductLike,ProductView,Wishlist,RecentlyViewed
# Register your models here.


admin.site.register(ProductView)
admin.site.register(ProductLike)
admin.site.register(Wishlist)
admin.site.register(RecentlyViewed)
