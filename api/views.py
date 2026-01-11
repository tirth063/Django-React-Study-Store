# utils/responses.py
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product, Like, Comment
from .serializers import UserRegistrationSerializer, UserDetailSerializer, ProductListSerializer, \
    ProductDetailSerializer, LikeSerializer


def api_success(message, data=None, status=200):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status)

def api_error(message, errors=None, status=400):
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return api_success(
                "User registered successfully",
                UserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return api_error("Validation error", serializer.errors)



class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password")
        )

        if not user:
            return api_error("Invalid username or password", status=401)

        token = RefreshToken.for_user(user)
        return api_success("Login successful", {
            "access": str(token.access_token),
            "refresh": str(token),
            "user": UserDetailSerializer(user).data
        })

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return api_success(
            "User profile",
            UserDetailSerializer(request.user).data
        )

class ProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductListSerializer(
            products, many=True, context={"request": request}
        )
        return api_success("Product list", serializer.data)

from rest_framework.permissions import IsAuthenticated
from .serializers import ProductCreateUpdateSerializer

class ProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(user=request.user)
            return api_success(
                "Product created",
                ProductListSerializer(product, context={"request": request}).data,
                status=201
            )
        return api_error("Validation error", serializer.errors)

from django.shortcuts import get_object_or_404

class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return api_success(
            "Product details",
            ProductDetailSerializer(product, context={"request": request}).data
        )

class ProductUpdateDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        serializer = ProductCreateUpdateSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_success("Product updated", serializer.data)
        return api_error("Validation error", serializer.errors)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk, user=request.user)
        product.delete()
        return api_success("Product deleted")

class LikeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LikeSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return api_success("Product liked")
        return api_error("Validation error", serializer.errors)

class LikeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        Like.objects.filter(
            user=request.user,
            product_id=product_id
        ).delete()
        return api_success("Like removed")

from .serializers import CommentSerializer

class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return api_success("Comment added", serializer.data)
        return api_error("Validation error", serializer.errors)


class CommentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        if comment.user != request.user:
            return api_error("You cannot delete this comment", status=403)
        comment.delete()
        return api_success("Comment deleted")

