from rest_framework.permissions import BasePermission
from rest_framework.decorators import action

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwner]

    def get_serializer_context(self):
        return {"request": self.request}


class ProductViewSet(ModelViewSet):

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        product = self.get_object()

        like, created = Like.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            like.delete()
            return Response({"liked": False})

        Notification.objects.create(
            user=product.user,
            message=f"{request.user.username} liked your product"
        )

        return Response({"liked": True})

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Comment.objects.filter(product_id=self.kwargs["product_pk"])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            product_id=self.kwargs["product_pk"]
        )

class NotificationViewSet(ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"read": True})


