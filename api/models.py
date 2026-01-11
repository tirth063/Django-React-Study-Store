from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.core.exceptions import ValidationError


def validate_image_size(image):
    max_size = 5 * 1024 * 1024  # 5MB
    if image.size > max_size:
        raise ValidationError(f'Image size cannot exceed 5MB. Current size: {image.size / (1024*1024):.2f}MB')


class Product(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Owner of the product'
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3, 'Title must be at least 3 characters long')],
        help_text='Product title'
    )
    description = models.TextField(
        validators=[MinLengthValidator(10, 'Description must be at least 10 characters long')],
        help_text='Detailed product description'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.title} by {self.user.username}'

    def clean(self):
        if self.title and self.title.strip() != self.title:
            raise ValidationError({'title': 'Title cannot have leading or trailing whitespace'})
        if self.description and len(self.description.strip()) < 10:
            raise ValidationError({'description': 'Description must be at least 10 characters long'})


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text='Product this image belongs to'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
                message='Only JPG, JPEG, PNG and WEBP images are allowed'
            ),
            validate_image_size
        ],
        help_text='Product image file'
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text='Alternative text for accessibility'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order')

    class Meta:
        ordering = ['order', 'uploaded_at']
        indexes = [
            models.Index(fields=['product', 'order']),
        ]

    def __str__(self):
        return f'Image for {self.product.title}'

    def clean(self):
        if not self.pk:
            existing_images = ProductImage.objects.filter(product=self.product).count()
            if existing_images >= 10:
                raise ValidationError('A product cannot have more than 10 images')


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text='User who liked the product'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text='Liked product'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} likes {self.product.title}'


class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='User who wrote the comment'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Product being commented on'
    )
    text = models.TextField(
        validators=[
            MinLengthValidator(1, 'Comment cannot be empty'),
        ],
        help_text='Comment text'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} on {self.product.title}'

    def clean(self):
        if self.text and len(self.text.strip()) < 1:
            raise ValidationError({'text': 'Comment cannot be empty or just whitespace'})
        if self.text and len(self.text) > 1000:
            raise ValidationError({'text': 'Comment cannot exceed 1000 characters'})