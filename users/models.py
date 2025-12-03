from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


class FriendshipRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_friend_requests",
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_friend_requests",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("from_user", "to_user")
        ordering = ["-created_at"]

    def accept(self):
        self.status = self.STATUS_ACCEPTED
        self.save()

    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save()

    def cancel(self):
        self.delete()

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"


class CustomUser(AbstractUser):
    """Custom user model with an optional profile picture."""
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("parent", "Parent"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    school_class = models.CharField(max_length=20, blank=False, null=False, help_text="Example: 10A, 4, 8A")

    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        null=True,
        blank=True,
        default="profile_pics/default_pic.jpeg",
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()}, {self.school_class})"

    def get_role_display(self):
        return self.role



    def friends(self):
        """Return a queryset of users who are friends (accepted requests)."""
        sent = FriendshipRequest.objects.filter(
            from_user=self, status=FriendshipRequest.STATUS_ACCEPTED
        ).values_list("to_user", flat=True)
        received = FriendshipRequest.objects.filter(
            to_user=self, status=FriendshipRequest.STATUS_ACCEPTED
        ).values_list("from_user", flat=True)
        user_ids = list(sent) + list(received)
        return CustomUser.objects.filter(id__in=user_ids)

    def is_friend_with(self, other_user):
        return FriendshipRequest.objects.filter(
            (
                models.Q(from_user=self, to_user=other_user)
                | models.Q(from_user=other_user, to_user=self)
            ),
            status=FriendshipRequest.STATUS_ACCEPTED,
        ).exists()
