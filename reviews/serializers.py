from rest_framework import serializers
from reviews.models import Review
from products.models import Product
from django.db.models import F



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','user','product','title','rating','comment']
        read_only_fields = ['id','user','product']

    
    
    def validate_rating(self, value):
        if not (0 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 0 and 5")
        return value
    

    def validate(self, data):
        user = self.context['user']
        product = self.context['product']

        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product"
            )

        return data


    def create(self, validated_data):
        product = self.context['product']
        user = self.context['user']



        product_reviews = Review.objects.create(
            product=product,
            user= user,
            **validated_data
        )


        # increment total_reviews safely
        Product.objects.filter(id=product.id).update(
            total_reviews=F('total_reviews') + 1
        )

        product.update_rating()

        return product_reviews