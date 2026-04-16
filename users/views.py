from django.shortcuts import render
from users.models import Company,Profile
from rest_framework.viewsets import ModelViewSet
from users.serializers import CompanySerializer,UserProfileSerializer
from django_filters.rest_framework import DjangoFilterBackend
# Create your views here.
from rest_framework.parsers import MultiPartParser, FormParser

    

class CompanyViewset(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name','email','address']




class ProfileViewSet(ModelViewSet):
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Profile.objects.none()
        return Profile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            company_id=self.kwargs.get('company_pk')  # only if exists
        )