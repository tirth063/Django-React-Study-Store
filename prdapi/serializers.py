from email_validator import validate_email, EmailNotValidError
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Comment, UserProfile, Like, Notification, Transaction


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class RegisterSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "balance"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise serializers.ValidationError("Invalid email")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        balance = validated_data.pop("balance")
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, balance=balance)
        return user

class CommentSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "user", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    comments = CommentSerializer(source="comment_set", many=True, read_only=True)

    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id","name","desc","price","image",
            "user","created_at",
            "like_count","comment_count",
            "is_liked_by_user","is_owner",
            "comments"
        ]

    def get_like_count(self, obj):
        return obj.like_set.count()

    def get_comment_count(self, obj):
        return obj.comment_set.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.like_set.filter(user=request.user).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return request and request.user.is_authenticated and obj.user_id == request.user.id


class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2)
    class Meta:
        model = User
        fields = ['id', 'username', 'email',"balance"]

    def validate_email(self, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise serializers.ValidationError("Invalid email format")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id"]

    def create(self, validated_data):
        user = self.context["request"].user
        product = self.context["product"]

        like, created = Like.objects.get_or_create(
            user=user,
            product=product
        )
        return like

class NotificationSerializer(serializers.ModelSerializer):
    from_user = UserMiniSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"

class TransactionSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    receiver = UserMiniSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"