import django_filters
from products.models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="versions__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="versions__price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['company', 'name', 'tech_stack', 'rating']