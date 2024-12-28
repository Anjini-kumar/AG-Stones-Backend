from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'mobile', 'gender', 'password', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},  
        }

    def create(self, validated_data):
        user_type = validated_data['user_type']
        
        # Create the user object
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            user_type=user_type,
            mobile=validated_data['mobile'],
            gender=validated_data['gender']
        )
        
        # Set the password
        user.set_password(validated_data['password'])
        
        # Set is_staff based on user_type
        if user_type == 'Admin':
            user.is_staff = True
        else:
            user.is_staff = False

        # Save the user
        user.save()
        return user

    def update(self, instance, validated_data):
        # Only set the password if it is provided
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            validated_data.pop('password')

        return super().update(instance, validated_data)



class ProductMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMaster
        fields = '__all__'

# class ProductSerializer(serializers.ModelSerializer):
#     product_master = serializers.PrimaryKeyRelatedField(queryset=ProductMaster.objects.all())

#     class Meta:
#         model = Product
#         fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'uploaded_at']

    def get_image(self, obj):
        request = self.context.get('request')  # Retrieve the request object
        if request:
            return request.build_absolute_uri(obj.image.url)  # Full URL for the image
        return obj.image.url  # Relative URL as fallback
    

class ProductVariantSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )  # Accept images as a list of file objects

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        # Extract images from validated data
        images_data = validated_data.pop('images', [])  # Default to an empty list
        product = Product.objects.create(**validated_data)  # Create product instance

        # Save each image
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)

        return product


class ReplySerializer(serializers.ModelSerializer):
    replied_by = serializers.CharField(source="replied_by.username", read_only=True)
    class Meta:
        model = Reply
        fields = ['id', 'request', 'message', 'replied_by', 'created_at']


class RequestSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.CharField(source="raised_by.username", read_only=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'raised_by_name', 'message', 'status', 'subject', 'created_at', 'replies']


class ReorderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reorder
        fields = '__all__'