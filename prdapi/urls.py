from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('products/public/', PublicProductListAPIView.as_view()),
    path('products/create/', ProductCreateAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailAPIView.as_view()),
    path('products/<int:pk>/like/', LikeProduct.as_view()),
    path('products/<int:pk>/comment/', AddComment.as_view()),
    path('products/<int:pk>/buy/', BuyProduct.as_view()),
    path('products/', ProductListAPIView.as_view()),
    path('notifications/', NotificationList.as_view()),
    path('notifications/<int:pk>/read/', MarkNotificationRead.as_view()),
    path('likes/', LikeHistory.as_view()),
    path('comments/', CommentHistory.as_view()),
    path('transactions/', TransactionHistory.as_view()),
]