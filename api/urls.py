from django.urls import path

from api.views import RegisterAPIView, LoginAPIView, UserDetailAPIView, ProductListAPIView, ProductCreateAPIView, \
    ProductDetailAPIView, ProductUpdateDeleteAPIView, LikeCreateAPIView, LikeDeleteAPIView, CommentCreateAPIView, \
    CommentDeleteAPIView

urlpatterns = [
    # Auth
    path("auth/register/", RegisterAPIView.as_view()),
    path("auth/login/", LoginAPIView.as_view()),
    path("auth/user/", UserDetailAPIView.as_view()),

    # Products
    path("products/", ProductListAPIView.as_view()),
    path("products/create/", ProductCreateAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),
    path("products/<int:pk>/edit/", ProductUpdateDeleteAPIView.as_view()),

    # Likes
    path("likes/", LikeCreateAPIView.as_view()),
    path("likes/<int:product_id>/", LikeDeleteAPIView.as_view()),

    # Comments
    path("comments/", CommentCreateAPIView.as_view()),
    path("comments/<int:pk>/", CommentDeleteAPIView.as_view()),
]
