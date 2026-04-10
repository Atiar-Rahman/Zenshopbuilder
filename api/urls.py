from django.urls import path,include
from rest_framework_nested import routers
from users.views import CompanyViewset,UserProfileViewset,ProfileViewSet
from products.views import CategoryViewSet,TachStackViewSet,TagViewSet,ProductViewSet,ProductVersionViewSet,ProductImageViewSet, ProductVersionImageViewSet



router = routers.DefaultRouter()
router.register('companies',CompanyViewset, basename='companies')
router.register('profile',UserProfileViewset,basename='profile')
router.register('category',CategoryViewSet, basename='category')
router.register('tachstack',TachStackViewSet,basename='tach-stack')
router.register('tag',TagViewSet,basename='tag')



# Nested router
companies_router = routers.NestedDefaultRouter(router, 'companies', lookup='company')
companies_router.register('employees', ProfileViewSet, basename='company-employees')
categories_router = routers.NestedDefaultRouter(router,'category',lookup='category')
categories_router.register('products',ProductViewSet,basename='products')


products_router = routers.NestedDefaultRouter(categories_router,'products',lookup='product')
products_router.register('version',ProductVersionViewSet, basename='version')
products_router.register('images',ProductImageViewSet,basename='images')

versions_router = routers.NestedDefaultRouter(products_router,'version', lookup='version')
versions_router.register('images',ProductVersionImageViewSet, basename='version-image')


urlpatterns = [
    path('',include(router.urls)),
    path('', include(companies_router.urls)),
    path('',include(categories_router.urls)),
    path('',include(products_router.urls)),
    path('',include(versions_router.urls))
]
