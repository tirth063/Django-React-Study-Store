# views.py
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegisterAPIView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')

            if not username:
                return Response({"error": "Username cannot be empty"}, status=400)

            if len(username) < 3 or len(username) > 50:
                return Response(
                    {"error": "Username must be 3 to 50 characters"},
                    status=400
                )

            if User.objects.filter(username=username).exists():
                return Response({"error": "Username already exists"}, status=400)

            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=400)

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return Response({"message": "User registered"}, status=201)

        except Exception:
            return Response(
                {"error": "Invalid input data"},
                status=400
            )

class ProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name = request.data.get('name')
            price = request.data.get('price')
            image = request.FILES.get('image')

            if not name:
                return Response({"error": "Product name required"}, status=400)

            if len(name) < 3:
                return Response({"error": "Product name too short"}, status=400)

            if not image:
                return Response({"error": "Product image is required"}, status=400)

            try:
                price = float(price)
                if price <= 0:
                    return Response({"error": "Price must be greater than 0"}, status=400)
            except:
                return Response({"error": "Price must be a number"}, status=400)

            product = Product.objects.create(
                name=name,
                price=price,
                image=image,
                user=request.user
            )

            return Response(ProductSerializer(product).data, status=201)

        except Exception:
            return Response({"error": "Invalid data"}, status=400)

class ProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({"error": "Not found"}, status=404)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({"error": "Not found"}, status=404)

        if product.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        name = request.data.get('name')
        price = request.data.get('price')

        if name:
            product.name = name

        if price:
            try:
                price = float(price)
                if price <= 0:
                    return Response({"error": "Invalid price"}, status=400)
                product.price = price
            except:
                return Response({"error": "Price must be number"}, status=400)

        product.save()
        return Response(ProductSerializer(product).data)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response({"error": "Not found"}, status=404)

        if product.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        product.delete()
        return Response({"message": "Deleted"})

class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            like, created = Like.objects.get_or_create(
                user=request.user,
                product_id=product_id
            )

            if not created:
                like.delete()
                return Response({"liked": False})

            if product.user != request.user:
                Notification.objects.create(
                    user=product.user,
                    message=f"{request.user.username} liked your product"
                )

            return Response({"liked": True})

        except Exception:
            return Response({"error": "Invalid request"}, status=400)

class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            content = request.data.get('content')
            product_id = request.data.get('product')

            if not content:
                return Response({"error": "Comment cannot be empty"}, status=400)

            comment = Comment.objects.create(
                content=content,
                product_id=product_id,
                user=request.user
            )

            if product.user != request.user:
                Notification.objects.create(
                    user=product.user,
                    message=f"{request.user.username} commented on your product"
                )

            return Response(CommentSerializer(comment).data, status=201)

        except Exception:
            return Response({"error": "Invalid data"}, status=400)

class ProductListAPIView(APIView):
    def get(self, request):
        search = request.GET.get('search')

        products = Product.objects.all()

        if search:
            products = products.filter(name__icontains=search)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

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

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')

        data = [
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at
            }
            for n in notifications
        ]

        return Response(data)

class NotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                pk=pk,
                user=request.user
            )
            notification.is_read = True
            notification.save()
            return Response({"message": "Marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
