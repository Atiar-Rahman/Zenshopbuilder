from django.contrib import admin
from orders.models import Cart,CartItem,Order,OrderItem
# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user']

    
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)


