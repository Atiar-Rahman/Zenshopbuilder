from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id','email','first_name','last_name','role']
        read_only_fields = ['role']
    

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id','email','first_name','last_name','role']
        read_only_fields=['role','email']

        def update(self, instance, validated_data):
            # Normal user can't update role
            validated_data.pop('role', None)
            return super().update(instance, validated_data)


class AdminUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id','email','first_name','last_name','role']