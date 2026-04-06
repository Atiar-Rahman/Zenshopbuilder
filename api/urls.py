from django.urls import path,include
from rest_framework_nested import routers
from users.views import CompanyViewset,UserProfileViewset,ProfileViewSet



router = routers.DefaultRouter()
router.register('companies',CompanyViewset, basename='companies')
router.register('profile',UserProfileViewset,basename='profile')

# Nested router
companies_router = routers.NestedDefaultRouter(router, 'companies', lookup='company')
companies_router.register('employees', ProfileViewSet, basename='company-employees')



urlpatterns = [
    path('',include(router.urls)),
    path('', include(companies_router.urls)),
]
