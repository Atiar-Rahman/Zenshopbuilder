from django.shortcuts import render
from users.models import Company,Profile
from rest_framework.viewsets import ModelViewSet
from users.serializers import CompanySerializer,UserProfoleSerializer
# Create your views here.


class CompanyViewset(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class UserProfileViewset(ModelViewSet):
    serializer_class = UserProfoleSerializer


    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            # Swagger reload or anonymous access → return empty queryset
            return Profile.objects.none()
        return Profile.objects.filter(user=user)
    



class ProfileViewSet(ModelViewSet):
    serializer_class = UserProfoleSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            # Swagger reload or anonymous access → return empty queryset
            return Profile.objects.none()
        return Profile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(company_id=self.kwargs.get('company_pk'))