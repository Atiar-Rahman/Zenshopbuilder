from django.contrib import admin
from orders.models import Cart,CartItem,Order,OrderItem,Address
# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user']

    
admin.site.register(CartItem)

@admin.register(Order)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer_name','status']

admin.site.register(OrderItem)

admin.site.register(Address)


