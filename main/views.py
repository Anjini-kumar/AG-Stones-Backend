from rest_framework import generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView




class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]



class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.objects.filter(email=email).first()
        print(user)
        print(email)
        print(user.user_type)
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_type': user.user_type,
                'user':user.username
            })
        return Response({'error': 'Invalid Credentials'}, status=400)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)




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
        products = Product.objects.all().select_related('product_master')

        # Use the existing ProductSerializer to serialize product data
        serialized_products = ProductSerializer(products, many=True).data

        # Add ProductMaster details to the serialized data
        for product in serialized_products:
            product_master_id = product["product_master"]
            # Fetch the related ProductMaster instance
            product_master = ProductMaster.objects.get(id=product_master_id)
            # Serialize ProductMaster using ProductMasterSerializer
            product["product_master"] = ProductMasterSerializer(product_master).data

        return Response(serialized_products)

# Create Product (only accessible by Admin and Procurement users)
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrProcurement]


class ProductDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        print(user,"dfs")
        # Fetch all products for Admin and Procurement
        products = Product.objects.all().select_related('product_master')
        print(user.user_type,"1223")
        # If the user is of type 'Warehouse', filter products by their warehouse
        if user.user_type == 'Warehouse':
            # Extract the part of the email before "@" and convert it to lowercase
            warehouse_name = user.email.split('@')[0].lower()
            print(warehouse_name,"warehouse name")
            # Convert warehouse choices to lowercase
            warehouse_choices = [choice[0].lower() for choice in Product.WAREHOUSE_CHOICES]
            print(warehouse_choices,"choices")
            # Check if the warehouse name matches a valid warehouse
            if warehouse_name in warehouse_choices:
                products = products.filter(warehouse__iexact=warehouse_name)
            else:
                 products = Product.objects.all().select_related('product_master')

        # Serialize product data
        serialized_products = ProductSerializer(products, many=True).data

        # Add related ProductMaster details to the serialized data
        for product in serialized_products:
            product_master_id = product["product_master"]
            # Fetch the related ProductMaster instance
            product_master = ProductMaster.objects.get(id=product_master_id)
            # Serialize ProductMaster using ProductMasterSerializer
            product["product_master"] = ProductMasterSerializer(product_master).data

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