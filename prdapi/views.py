from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Like, Comment, Notification, Transaction
from .serializers import ProductSerializer, RegisterSerializer, NotificationSerializer
from .permissions import IsOwner


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "balance": user.profile.balance
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=201)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "balance": user.profile.balance
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

class PublicProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.select_related("user").prefetch_related("like_set","comment_set")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {"request": self.request}

class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        name = serializer.validated_data["name"]

        if Product.objects.filter(name__iexact=name).exists():
            raise ValidationError({"name": "Product already exists"})

        serializer.save(user=self.request.user)

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsOwner()]

    def get_serializer_context(self):
        return {"request": self.request}

class LikeProduct(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        like, created = Like.objects.get_or_create(
            user=request.user, product=product
        )

        if created and product.user != request.user:
            Notification.objects.create(
                from_user=request.user,
                to_user=product.user,
                message=f"{request.user.username} liked your product"
            )

        return Response({"liked": True})

class AddComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        Comment.objects.create(
            user=request.user,
            product=product,
            content=request.data.get("content")
        )

        if product.user != request.user:
            Notification.objects.create(
                from_user=request.user,
                to_user=product.user,
                message=f"{request.user.username} commented on your product"
            )

        return Response({"status": "commented"})

class BuyProduct(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        buyer = request.user
        seller = product.user

        if buyer == seller:
            return Response(
                {"error": "You cannot buy your own product"},
                status=400
            )

        if buyer.profile.balance < product.price:
            return Response({"error": "Insufficient balance"}, status=400)

        buyer.profile.balance -= product.price
        seller.profile.balance += product.price
        buyer.profile.save()
        seller.profile.save()

        Transaction.objects.create(
            product=product,
            sender=buyer,
            receiver=seller,
            amount=product.price,
            tx_type="withdraw"
        )

        Notification.objects.create(
            from_user=buyer,
            to_user=seller,
            message=f"{buyer.username} bought your product"
        )

        return Response({"status": "purchased"})

class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()

        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        my_products = request.GET.get('my_products')

        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                return Response(
                    {"error": "min_price must be a number"},
                    status=400
                )

        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                return Response(
                    {"error": "max_price must be a number"},
                    status=400
                )

        if my_products == "true" and request.user.is_authenticated:
            products = products.filter(user=request.user)

        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)

class NotificationList(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            to_user=self.request.user
        ).order_by("-created_at")

class MarkNotificationRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        n = Notification.objects.get(pk=pk, to_user=request.user)
        n.status = "read"
        n.save()
        return Response({"status":"read"})

class LikeHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Like.objects.select_related("product").filter(user=request.user)
        return Response([{"product": l.product.name} for l in qs])

class CommentHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Comment.objects.select_related("product").filter(user=request.user)
        return Response([{"product": c.product.name, "content": c.content} for c in qs])

class TransactionHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.select_related("product").filter(Q(sender=request.user) | Q(receiver=request.user))
        return Response([{
            "product": t.product.name if t.product else None,
            "amount": t.amount,
            "type": t.tx_type,
            "date": t.created_at
        } for t in qs])
