from django.urls import path
from .views import *

urlpatterns = [
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UpdateUserView.as_view(), name='update-user'),
    path('users1/<int:pk>/', DeleteUserView.as_view(), name='delete-user'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),


    #products
    path('product/', ProductListView.as_view(), name='product-list'),
    path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/', ProductDetailView.as_view(), name='product-detail'),
    path('product/update/<int:id>/', ProductUpdateView.as_view(), name='product-update'),
    path('product/delete/<int:id>/', ProductDeleteView.as_view(), name='product-delete'),
    path('product/<int:product_id>/comment/', UpdateProductCommentView.as_view(), name='update-product-comment'),
    path('product/<int:product_id>/add-images/', ProductImageUploadView.as_view(), name='product-add-images'),

    # path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    # path('products/<int:pk>/', ProductRetrieveUpdateDeleteView.as_view(), name='product-detail'),

    path('product-master/', ProductMasterListView.as_view(), name='product-master-list'),
    path('product-master/create/', ProductMasterCreateView.as_view(), name='product-master-create'),
    path('product-master/delete/<int:id>/', ProductMasterDeleteView.as_view(), name='product-master-delete'),

    path('products/<int:product_id>/images/', ProductImagesView.as_view(), name='product-images'),
    path('products/<int:pk>/status/', ProductStatusUpdateView.as_view(), name='product-status-update'),
    path('products/<int:pk>/action/', ProductActionUpdateView.as_view(), name='product-action-update'),



    path('requests/', RequestListView.as_view(), name='list-requests'),
    path('requests/create/', CreateRequestView.as_view(), name='create-request'),
    path('replies/create/', CreateReplyView.as_view(), name='create-reply'),


    path('reorders/', ReorderListView.as_view(), name='reorder-list'),
    path('reorders/create/', ReorderCreateView.as_view(), name='reorder-create'),

    path('productsapproves/', ApprovedProductsView.as_view(), name='approved-products'),
    path('productsstatus/<int:pk>/', UpdateProductStatusView.as_view(), name='update-product-status'),


]
