from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from users.models import Company, Profile






class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id','email','first_name','password','last_name','role']
        read_only_fields = ['role']
    

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id','email','first_name','last_name','role','is_staff']
        read_only_fields=['role','email']

        def update(self, instance, validated_data):
            # Normal user can't update role
            validated_data.pop('role', None)
            return super().update(instance, validated_data)


class AdminUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id','email','first_name','last_name','role']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model=Company
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    company = serializers.PrimaryKeyRelatedField(
    queryset=Company.objects.all()
    )
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            'id','user','company','profile_image','bio',
            'gender','present_address','permanent_address',
            'city','country'
        ]
        read_only_fields = ['user','company']


