from rest_framework import generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import *
from .serializers import *
import requests
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import update_last_login
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView
from django.contrib.auth import authenticate
from django.conf import settings




class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        
        # Validate old password
        old_password = data.get('old_password')
        if not user.check_password(old_password):
            return Response({'old_password': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and set new password
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if new_password != confirm_password:
            return Response({'new_password': 'New password and confirm password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Optionally update the last login timestamp
        update_last_login(None, user)

        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        recaptcha_response = request.data.get('recaptcha')

        # Verify reCAPTCHA
        recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
        recaptcha_data = {
            "secret": settings.RECAPTCHA_SECRET_KEY,  # Use the secret key from settings
            "response": recaptcha_response,
        }
        recaptcha_verify = requests.post(recaptcha_url, data=recaptcha_data)
        recaptcha_result = recaptcha_verify.json()

        if not recaptcha_result.get("success"):
            return Response(
                {"error": "Invalid reCAPTCHA. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate the user
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_type": user.user_type,
                    "user": user.username,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class UpdateUserView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        if user.user_type != 'Admin':
            raise PermissionDenied("You do not have permission to edit users.")
        return super().partial_update(request, *args, **kwargs)


class DeleteUserView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.user_type != 'Admin':
            raise PermissionDenied("You do not have permission to delete users.")
        return super().delete(request, *args, **kwargs)



class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 'Admin':
            users = CustomUser.objects.all()
        else:
            users = CustomUser.objects.filter(id=user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    


class IsAdminOrProcurement(permissions.BasePermission):
    """
    Custom permission to only allow users with 'Admin' or 'Procurement' user_type to access the view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and if their user_type is either 'Admin' or 'Procurement'
        return request.user.is_authenticated and request.user.user_type in ['Admin', 'Procurement']

#product master views

class ProductMasterCreateView(generics.CreateAPIView):
    queryset = ProductMaster.objects.all()
    serializer_class = ProductMasterSerializer
    permission_classes = [IsAdminOrProcurement]  


# Delete ProductMaster
class ProductMasterDeleteView(generics.DestroyAPIView):
    queryset = ProductMaster.objects.all()
    serializer_class = ProductMasterSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminOrProcurement]  

# List ProductMaster 
class ProductMasterListView(generics.ListAPIView):
    queryset = ProductMaster.objects.all()
    serializer_class = ProductMasterSerializer
    permission_classes = [IsAdminOrProcurement] 

#product views
class ProductListView(APIView):
    permission_classes = [IsAdminOrProcurement]

    def get(self, request, *args, **kwargs):
        # Fetch all products
        products = Product.objects.all()

        # Use the existing ProductSerializer to serialize product data
        serialized_products = ProductSerializer(products, many=True).data

        return Response(serialized_products)

# Create Product (only accessible by Admin and Procurement users)
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrProcurement]


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is a Warehouse user
        if user.user_type == 'Warehouse':
            # Get the sub_user_type of the Warehouse user
            sub_user_type = user.sub_user_type

            # Fetch products based on the sub_user_type
            if sub_user_type:
                # Check if sub_user_type matches any valid warehouse choice
                valid_choices = [choice[0] for choice in Product.WAREHOUSE_CHOICES]
                if sub_user_type in valid_choices:
                    # Fetch products specific to the sub_user_type and 'All' category
                    products = Product.objects.filter(
                        warehouse=sub_user_type
                    ) | Product.objects.filter(warehouse='All')
                else:
                    return Response({"error": "Invalid sub_user_type."}, status=400)
            else:
                return Response({"error": "sub_user_type is required for Warehouse users."}, status=400)
        else:
            # Fetch all products for Admin and Procurement users
            products = Product.objects.all()

        # Serialize the product data
        serialized_products = ProductSerializer(products, many=True).data

        return Response(serialized_products)

# Update Product (only accessible by Admin and Procurement users)
class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrProcurement]
    lookup_field = 'id'

# Delete Product (only accessible by Admin and Procurement users)
class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrProcurement]
    lookup_field = 'id'


class UpdateProductCommentView(APIView):
    def patch(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        images = request.FILES.getlist('images')  # Handle multiple images
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for image in images:
            product_image = ProductImage(product=product, image=image)
            product_image.save()
            created_images.append(ProductImageSerializer(product_image).data)

        return Response({'images': created_images}, status=status.HTTP_201_CREATED)
    

class ProductImagesView(APIView):
    def get(self, request, product_id):
        try:
            # Retrieve the product by its ID
            product = Product.objects.get(id=product_id)

            # Retrieve all images related to the product
            images = ProductImage.objects.filter(product=product)

            # Serialize the image data
            serializer = ProductImageSerializer(images, many=True, context={'request': request})

            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        


class ProductStatusUpdateView(APIView):
    def get(self, request, pk):
        """
        Retrieve product details by ID.
        """
        product = get_object_or_404(Product, pk=pk)
        product_data = {
            "id": product.id,
            "product_master": ProductMasterSerializer(product.product_master).data,
            "status": product.status,
            "block_no": product.block_no,
            "bundles": product.bundles,
            "warehouse": product.warehouse,
        }
        return Response(product_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Update the status of a product by ID.
        """
        product = get_object_or_404(Product, pk=pk)
        new_status = request.data.get("status")
        if new_status not in dict(Product.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status choice."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.status = new_status
        product.save()
        return Response({"message": "Status updated successfully."}, status=status.HTTP_200_OK)

class ProductActionUpdateView(APIView):
    def get(self, request, pk):
        """
        Retrieve product details by ID.
        """
        product = get_object_or_404(Product, pk=pk)
        product_data = {
            "id": product.id,
            "product_master": ProductMasterSerializer(product.product_master).data,
            "action": product.action,
            "block_no": product.block_no,
            "bundles": product.bundles,
            "warehouse": product.warehouse,
        }
        return Response(product_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Update the status of a product by ID.
        """
        product = get_object_or_404(Product, pk=pk)
        new_action = request.data.get("action")
        if new_action not in dict(Product.ACTION_CHOICES):
            return Response(
                {"error": "Invalid action choice."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product.action = new_action
        product.save()
        return Response({"message": "Action updated successfully."}, status=status.HTTP_200_OK)
    


class RequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the user is of type 'Warehouse'
        if request.user.user_type == 'Warehouse':
            # Fetch only the requests raised by the Warehouse user
            requests = Request.objects.filter(raised_by=request.user).prefetch_related('replies')
        else:
            # Fetch all requests for other user types
            requests = Request.objects.all().prefetch_related('replies', 'raised_by')

        # Serialize the data
        serialized_requests = RequestSerializer(requests, many=True).data

        return Response(serialized_requests, status=status.HTTP_200_OK)



class CreateRequestView(CreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Check if the user type is 'warehouse'
        print(self.request.user.user_type,"usertype")
        if self.request.user.user_type == 'Warehouse':
            serializer.save(raised_by=self.request.user)
        else:
            # Raise an exception or handle the case where the user is not allowed
            raise PermissionDenied("Only users with warehouse access can raise a request.")


class CreateReplyView(CreateAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(replied_by=self.request.user)


class ReorderListView(generics.ListAPIView):
    queryset = Reorder.objects.all()
    serializer_class = ReorderSerializer
    permission_classes = [IsAuthenticated]

class ReorderCreateView(generics.CreateAPIView):
    queryset = Reorder.objects.all()
    serializer_class = ReorderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.user_type == 'Warehouse':
            serializer.save()
        else:
            raise serializers.ValidationError("You do not have permission to create a reorder.")
        


class ApprovedProductsView(APIView):
    def get(self, request):
        approved_products = Product.objects.filter(action='Approved').prefetch_related('images')  # Prefetch images
        serializer = ProductVariantSerializer(
            approved_products, many=True, context={'request': request}  # Pass the request context
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

# Update Product Status and Status Text
class UpdateProductStatusView(APIView):
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)