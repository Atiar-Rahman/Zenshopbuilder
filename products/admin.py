from django.contrib import admin
from products.models import Category,TechStack,ProductVersion,Tag
# Register your models here.

admin.site.register(Category)
admin.site.register(TechStack)
admin.site.register(ProductVersion)
admin.site.register(Tag)
    