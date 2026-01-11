from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Product, ProductImage, Like, Comment
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True}
        }

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                'Username can only contain letters, numbers, and underscores'
            )
        if len(value) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters long')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered')
        return value.lower()

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'products_count')
        read_only_fields = ('id', 'username', 'email', 'date_joined')

    def get_products_count(self, obj):
        return obj.products.count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'order', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')

    def validate_image(self, value):
        if value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError('Image size cannot exceed 5MB')

        # Validate file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'Invalid file extension. Allowed: {", ".join(allowed_extensions)}'
            )
        return value

    def validate_order(self, value):
        if value <= 0:
            raise serializers.ValidationError('Order must be non-negative')
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'username', 'product', 'text', 'created_at', 'updated_at', 'is_owner')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Comment cannot be empty')
        if len(value.strip()) < 1:
            raise serializers.ValidationError('Comment must have at least 1 character')
        if len(value) > 1000:
            raise serializers.ValidationError('Comment cannot exceed 1000 characters')
        return value.strip()


class ProductListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'user_id', 'username',
            'images', 'like_count', 'comment_count',
            'is_liked_by_user', 'is_owner', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False


class ProductDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'user_id', 'username',
            'images', 'comments', 'like_count', 'comment_count',
            'is_liked_by_user', 'is_owner', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'images', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty')
        if len(value.strip()) < 3:
            raise serializers.ValidationError('Title must be at least 3 characters long')
        if len(value) > 200:
            raise serializers.ValidationError('Title cannot exceed 200 characters')
        return value.strip()

    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Description cannot be empty')
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Description must be at least 10 characters long')
        if len(value) > 5000:
            raise serializers.ValidationError('Description cannot exceed 5000 characters')
        return value.strip()

    def create(self, validated_data):
        """Create product with user from context"""
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product

    def update(self, instance, validated_data):
        """Update product (images handled separately)"""
        validated_data.pop('images', None)  # Images updated via separate endpoint
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_details = serializers.SerializerMethodField()
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'username', 'user_details', 'product', 'product_title', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'full_name': f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        }

    def validate(self, attrs):
        request = self.context.get('request')
        product = attrs.get('product')

        if Like.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError('You have already liked this product')

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        return Like.objects.create(user=request.user, **validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    current_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, required=False, min_length=8,
                                         style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'current_password', 'new_password', 'new_password_confirm')

    def validate_email(self, value):
        user = self.instance
        if value != user.email and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use')
        return value.lower()

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        current_password = attrs.get('current_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password:
            if not current_password:
                raise serializers.ValidationError({
                    'current_password': 'Current password is required to set new password'
                })

            if not self.instance.check_password(current_password):
                raise serializers.ValidationError({
                    'current_password': 'Current password is incorrect'
                })

            if new_password != new_password_confirm:
                raise serializers.ValidationError({
                    'new_password_confirm': 'New passwords do not match'
                })

            try:
                validate_password(new_password, self.instance)
            except DjangoValidationError as e:
                raise serializers.ValidationError({
                    'new_password': list(e.messages)
                })

        return attrs

    def update(self, instance, validated_data):
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('new_password_confirm', None)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance


class ProductStatsSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    view_count = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'like_count', 'comment_count', 'is_liked_by_user', 'view_count')

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class ProductImageBulkSerializer(serializers.Serializer):
    """Serializer for bulk image upload"""
    images = serializers.ListField(
        child=serializers.ImageField(
            validators=[
                FileExtensionValidator(
                    allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
                    message='Only JPG, JPEG, PNG and WEBP images are allowed'
                )
            ]
        ),
        allow_empty=False,
        max_length=10
    )
    alt_texts = serializers.ListField(
        child=serializers.CharField(max_length=200, allow_blank=True),
        required=False,
        allow_empty=True
    )

    def validate_images(self, value):
        for image in value:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise serializers.ValidationError(
                    f'Image {image.name} exceeds 5MB size limit'
                )
        return value

    def validate(self, attrs):
        images = attrs.get('images', [])
        alt_texts = attrs.get('alt_texts', [])

        if alt_texts and len(alt_texts) != len(images):
            raise serializers.ValidationError(
                'Number of alt_texts must match number of images'
            )

        product = self.context.get('product')
        if product:
            existing_count = product.images.count()
            if existing_count + len(images) > 10:
                raise serializers.ValidationError(
                    f'Cannot upload {len(images)} images. Product has {existing_count} images. Maximum is 10.'
                )

        return attrs


class CommentNestedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'username', 'user_avatar', 'text', 'created_at')

    def get_user_avatar(self, obj):
        return None


class UserPublicSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    total_likes_received = serializers.SerializerMethodField()
    total_comments_made = serializers.SerializerMethodField()
    member_since = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'products_count', 'total_likes_received', 'total_comments_made',
            'member_since'
        )

    def get_products_count(self, obj):
        return obj.products.count()

    def get_total_likes_received(self, obj):
        return Like.objects.filter(product__user=obj).count()

    def get_total_comments_made(self, obj):
        return obj.comments.count()


class ProductMinimalSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    thumbnail = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'username', 'thumbnail', 'like_count', 'created_at')

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None

    def get_like_count(self, obj):
        return obj.likes.count()


class ProductSearchSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    thumbnail = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    relevance_score = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'title', 'username', 'thumbnail', 'excerpt', 'created_at', 'relevance_score')

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
        return None

    def get_excerpt(self, obj):
        if len(obj.description) <= 150:
            return obj.description
        return obj.description[:150] + '...'


class CommentWithRepliesSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    is_owner = serializers.SerializerMethodField()
    is_product_owner = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id', 'user', 'username', 'product', 'text',
            'created_at', 'updated_at', 'is_owner', 'is_product_owner',
            'can_edit', 'can_delete'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def get_is_product_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.product.user == request.user
        return False

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user or obj.product.user == request.user
        return False

    def validate_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Comment cannot be empty')
        if len(value.strip()) < 1:
            raise serializers.ValidationError('Comment must have at least 1 character')
        if len(value) > 1000:
            raise serializers.ValidationError('Comment cannot exceed 1000 characters')
        return value.strip()


class ProductWithUserSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    latest_comments = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'user', 'images',
            'like_count', 'comment_count', 'is_liked_by_user',
            'is_owner', 'latest_comments', 'created_at', 'updated_at'
        )

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False

    def get_latest_comments(self, obj):
        latest = obj.comments.select_related('user').order_by('-created_at')[:3]
        return CommentNestedSerializer(latest, many=True).data