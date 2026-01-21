from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    desc = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'product')

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    STATUS_CHOICES = (
        ("read", "Read"),
        ("unread", "Unread"),
    )

    message = models.CharField(max_length=255)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_notifications")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unread")
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TX_TYPE = (
        ("deposit", "Deposit"),
        ("withdraw", "Withdraw"),
    )

    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_transactions")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tx_type = models.CharField(max_length=10, choices=TX_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
