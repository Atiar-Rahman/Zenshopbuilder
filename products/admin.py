from django.contrib import admin
from products.models import Category,TechStack,ProductVersion,Tag,ProductImage,Product,ProductVersionImage
# Register your models here.

admin.site.register(Category)
admin.site.register(TechStack)

@admin.register(ProductVersion)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','product']


admin.site.register(Tag)
admin.site.register(ProductVersionImage)
admin.site.register(ProductImage)
admin.site.register(Product)
    