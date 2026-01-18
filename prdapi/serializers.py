from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProductSerializer(serializers.ModelSerializer):
    # WRITE SIDE (server controlled)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # READ SIDE (for homepage)
    owner = serializers.SlugRelatedField(
        source='user',
        slug_field='username',
        read_only=True
    )
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'owner', 'user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    username = serializers.SlugRelatedField(
        source='user',
        slug_field='username',
        read_only=True
    )

class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'product', 'username']

