from rest_framework import serializers
from products.models import Category,Product,ProductImage,ProductVersion,TechStack,Tag,ProductVersionImage
from users.serializers import CompanySerializer

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
        ]
        read_only_fields = [
            'id',
            'slug',
            'created_by',
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

class ProductVersionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVersionImage
        fields = ['id','product_version','image','caption','created_at','created_by','is_deleted','deleted_at']
        read_only_fields = ['id','created_at','created_by','is_deleted','deleted_at']

    def create(self,validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        version_id = self.context.get('version_id')

        if not version_id:
            raise serializers.ValidationError({'message':'version_id must be needed'})
        
        version_images = ProductVersionImage.objects.create(
            created_by = user,
            product_version_id = version_id,
            **validated_data
        )
        return version_images
    

class ProductVersionSerializer(serializers.ModelSerializer):
    version_image = ProductVersionImageSerializer(source = 'version_images',read_only=True, many=True)
    class Meta:
        model = ProductVersion
        fields = [
            'id', 'version', 'license_type', 'price', 'discount_price',
            'file', 'release_date', 'changelog', 'docs_url', 'download_count',
            'is_active', 'is_featured', 'is_deleted', 'created_by', 'deleted_by', 'deleted_at','product','version_image'
        ]
        read_only_fields = ['id', 'download_count', 'created_by', 'deleted_by', 'deleted_at','version_image']

    def create(self,validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        product_id = self.context.get('product_id')

        if not product_id:
            raise serializers.ValidationError({'message':'product_id not found'})
        
        product_version = ProductVersion.objects.create(
            created_by = user,
            product_id = product_id,
            **validated_data
        )
        return product_version


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'is_main', 'is_deleted', 'created_by', 'deleted_by', 'deleted_at']
        read_only_fields = ['id', 'created_by', 'deleted_by', 'deleted_at']

    def create(self, validated_data):
        request = self.context.get('request')
        product_id = self.context.get('product_id')

        if not product_id:
            raise serializers.ValidationError({'message':'product slug must be set'})
        
        product_image = ProductImage.objects.create(
            created_by=request.user,
            product_id=product_id,
            **validated_data
        )

        return product_image


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','thumbnail','live_preview_url','status','short_description']



class ProductDetailSerializer(serializers.ModelSerializer):
    product_image = ProductImageSerializer(source = 'images' ,many=True, read_only=True)
    product_version = ProductVersionSerializer(source='versions',many=True, read_only=True)

    tech_stack = serializers.PrimaryKeyRelatedField(
        queryset=TechStack.objects.filter(is_deleted=False),
        many=True,
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.filter(is_deleted=False),
        many=True,
        required=False
    )
    # Read using names
    tech_stack_names = serializers.StringRelatedField(
        source='tech_stack',
        many=True,
        read_only=True
    )
    tag_names = serializers.StringRelatedField(
        source='tags',
        many=True,
        read_only=True
    )
    # Category name instead of ID
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'description',
            'thumbnail', 'live_preview_url', 'status', 'is_active',
            'total_sales', 'total_views', 'rating', 'total_reviews',
            'category', 'category_name',  # ID for write, name for read
            'tech_stack', 'tech_stack_names',
            'tags', 'tag_names','product_image','product_version'
        ]
        read_only_fields = [
            'id','slug','deleted_by','created_by','created_at','deleted_at',
            'total_sales','total_views','rating','total_reviews',
            'category_name','tech_stack_names','tag_names','product_image','product_version'
        ]

    def create(self, validated_data):
        tech_stack_data = validated_data.pop('tech_stack', [])
        tags_data = validated_data.pop('tags', [])

        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            user = None

        category_id = self.context.get('category_id')
        if not category_id:
            raise serializers.ValidationError("Category is required")

        product = Product.objects.create(
            created_by=user,
            category_id=category_id,
            **validated_data
        )

        if tech_stack_data:
            product.tech_stack.set(tech_stack_data)

        if tags_data:
            product.tags.set(tags_data)

        return product

    def update(self, instance, validated_data):
        tech_stack_data = validated_data.pop('tech_stack', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tech_stack_data is not None:
            instance.tech_stack.set(tech_stack_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        instance.save()
        return instance


