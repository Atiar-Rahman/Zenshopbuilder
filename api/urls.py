from django.urls import path,include
from rest_framework_nested import routers
from users.views import CompanyViewset,ProfileViewSet
from products.views import CategoryViewSet,TechStackViewSet,TagViewSet,ProductViewSet,ProductVersionViewSet,ProductImageViewSet, ProductVersionImageViewSet,RestoreCategoryViewSet,RestoreTeckStackViewSet,RestoreTagViewSet,RestoreProductViewSet,RestoreProductImageViewSet,RestoreProductVersionImageViewSet,RestoreProductVersionViewSet, ProductDetailViewSet,ProductCompareViewSet
from orders.views import CartViewSet, CartItemViewSet,OrderViewSet
from reviews.views import ReviewViewSet
from interactions.views import HistoryViewSet

router = routers.DefaultRouter()
router.register('companies',CompanyViewset, basename='companies')
router.register('category',CategoryViewSet, basename='category')
router.register('category-restore',RestoreCategoryViewSet,basename='restore-category')
router.register('products',ProductViewSet,basename='products')
router.register('product-compare',ProductCompareViewSet, basename='product-compare')
router.register('techstack',TechStackViewSet,basename='tech-stack')
router.register('techstack-restore',RestoreTeckStackViewSet,basename='restore-techstack')
router.register('tag',TagViewSet,basename='tag')
router.register('tag-restore', RestoreTagViewSet, basename='restore-tag')
router.register('product-restore', RestoreProductViewSet, basename='restore-product')
router.register('version-restore', RestoreProductVersionViewSet, basename='restore-version')
router.register('product-image-restore', RestoreProductImageViewSet, basename='restore-product-image')
router.register('version-image-restore', RestoreProductVersionImageViewSet, basename='restore-version-image')
router.register('carts', CartViewSet, basename='carts')
router.register('orders',OrderViewSet, basename='orders')
router.register('histories',HistoryViewSet,basename='hostory')


# Nested router
companies_router = routers.NestedDefaultRouter(router, 'companies', lookup='company')
companies_router.register('employees', ProfileViewSet, basename='company-employees')
companies_router.register('profile',ProfileViewSet,basename='profile')

categories_router = routers.NestedDefaultRouter(router,'category',lookup='category')
categories_router.register('products',ProductDetailViewSet,basename='products')


products_router = routers.NestedDefaultRouter(categories_router,'products',lookup='product')
products_router.register('version',ProductVersionViewSet, basename='version')
products_router.register('images',ProductImageViewSet,basename='images')
products_router.register('reviews', ReviewViewSet, basename='product-reviews')

versions_router = routers.NestedDefaultRouter(products_router,'version', lookup='version')
versions_router.register('images',ProductVersionImageViewSet, basename='version-image')

carts_router = routers.NestedDefaultRouter(router,'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('',include(router.urls)),
    path('', include(companies_router.urls)),
    path('',include(categories_router.urls)),
    path('',include(products_router.urls)),
    path('',include(versions_router.urls)),
    path('',include(carts_router.urls)),
]
