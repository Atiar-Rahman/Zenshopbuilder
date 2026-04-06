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
        return Profile.objects.filter(user=self.request.user)
    



class ProfileViewSet(ModelViewSet):
    serializer_class = UserProfoleSerializer

    def get_queryset(self):
        return Profile.objects.filter(company_id=self.kwargs['company_pk'])

    def perform_create(self, serializer):
        serializer.save(company_id=self.kwargs['company_pk'])