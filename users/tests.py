from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, get_user

User = get_user_model()


class LogoutTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
        )
        self.user.set_password("testpassword")
        self.user.save()

    def test_logout(self):
        self.client.login(username="testuser", password="testpassword")
        self.client.get(reverse("users:logout"))
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)


class ProfileTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
        )
        self.user.set_password("testpassword")
        self.user.save()

    def test_login_required(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("users:login") + "?next=" + reverse("users:profile")
        )

    def test_profile_page(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")
        self.assertContains(response, "User")
        self.assertContains(response, "testuser@example.com")
        self.assertContains(response, "testuser")

    def test_profile_update_page(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("users:profile_update"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Profile")

    def test_profile_update(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            reverse("users:profile_update"),
            data={
                "username": "updateduser",
                "first_name": "Updated",
                "last_name": "User",
                "email": "updateduser@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.username, "updateduser")
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.email, "updateduser@example.com")
        self.assertRedirects(response, reverse("users:profile"))
