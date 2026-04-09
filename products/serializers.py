from rest_framework import serializers
from products.models import Category,Product,ProductImage,ProductVersion,TechStack,Tag


class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=Category.active_objects.filter(is_deleted=False),
        allow_null=True,
        required=False
    )
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'image',
            'is_active',
            'parent',
            'parent_id',
            'is_deleted',
            'created_by',
            'deleted_by',
            'deleted_at'
        ]
        read_only_fields = [
            'id',
            'slug',
            'created_by',
            'deleted_by',
            'deleted_at'
        ]

    #  Parent short representation
    def get_parent(self, obj):
        if obj.parent:
            return {
                "id": obj.parent.id,
                "name": obj.parent.name,
                "slug": obj.parent.slug
            }
        return None

    #  Prevent self-parent
    def validate_parent(self, value):
        if self.instance and value == self.instance:
            raise serializers.ValidationError("Category cannot be its own parent.")
        return value

    #  Depth limit protection (avoid infinite nesting)
    def validate(self, data):
        parent = data.get('parent')
        depth = 0

        while parent:
            depth += 1
            if depth > 5:
                raise serializers.ValidationError("Max category depth exceeded (5).")
            parent = parent.parent

        return data

    #  CREATE (model handles slug)
    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            user = None
        
        # remove slug if sent from client
        validated_data.pop('slug', None)

        return Category.objects.create(
            created_by=user,
            **validated_data
        )

    #  UPDATE (model handles slug regeneration)
    def update(self, instance, validated_data):
        # prevent manual slug override
        validated_data.pop('slug', None)

        # update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # if name changed → regenerate slug via model
        if 'name' in validated_data:
            instance.slug = None   # triggers model slug logic

        instance.save()
        return instance
    
class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = ['id','name','is_deleted','created_by','deleted_by','deleted_at','created_at']
        read_only_fields = ['id','created_by','deleted_by','created_at','deleted_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            user = None
            
        return TechStack.objects.create(
            created_by=user,
            **validated_data
        )
    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag 
        fields = ['id','name','is_deleted','created_by','deleted_by','deleted_at','created_at']
        read_only_fields = ['id','created_by','deleted_by','created_at','deleted_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            user = None
            
        return Tag.objects.create(
            created_by=user,
            **validated_data
        )

