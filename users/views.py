from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import get_user_model
from users.forms import UserCreateForm, UserUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import login, logout
from django.urls import reverse

User = get_user_model()


# ---Registration Section---
class RegisterView(View):
    def get(self, request):
        create_form = UserCreateForm()
        context = {"form": create_form}

        return render(request, "users/register.html", context)

    def post(self, request):
        create_form = UserCreateForm(data=request.POST)

        if create_form.is_valid():
            create_form.save()
            return redirect("users:login")
        else:
            context = {"form": create_form}
            return render(request, "users/register.html", context=context)


# ---Login / Logout Section---
class LoginView(View):
    def get(self, request):
        login_form = AuthenticationForm()
        return render(request, "users/login.html", {"login_form": login_form})

    def post(self, request):
        login_form = AuthenticationForm(data=request.POST)
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect("books:list")
        else:
            return render(request, "users/login.html", {"login_form": login_form})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("landing_page")


# ---Profile Section---
class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "users/profile.html", {"user": request.user})


class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        user_update_form = UserUpdateForm(instance=request.user)
        return render(request, "users/profile_update.html", {"form": user_update_form})

    def post(self, request):
        user_update_form = UserUpdateForm(
            data=request.POST, files=request.FILES, instance=request.user
        )
        if user_update_form.is_valid():
            user_update_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("users:profile"))
        else:
            return render(
                request, "users/profile_update.html", {"form": user_update_form}
            )


# ---------------- Friend System Views ----------------
class SendFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        to_user = get_user_model().objects.filter(pk=pk).first()
        if not to_user:
            messages.error(request, "User not found.")
            return redirect("users:friends_list")
        if to_user == request.user:
            messages.error(request, "You cannot send a friend request to yourself.")
            return redirect("users:friends_list")

        # Check existing
        existing = users_models = None
        from users.models import FriendshipRequest

        try:
            existing = FriendshipRequest.objects.get(
                from_user=request.user, to_user=to_user
            )
        except FriendshipRequest.DoesNotExist:
            existing = None

        if existing:
            if existing.status == FriendshipRequest.STATUS_PENDING:
                messages.info(request, "Friend request already sent.")
            elif existing.status == FriendshipRequest.STATUS_ACCEPTED:
                messages.info(request, "You are already friends.")
            else:
                messages.info(request, "A previous request was rejected.")
            return redirect("users:friends_list")

        # Make new request
        FriendshipRequest.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, "Friend request sent.")
        return redirect("users:friends_list")


class RespondFriendRequestView(LoginRequiredMixin, View):
    def post(self, request, pk, action=None):
        from users.models import FriendshipRequest

        fr = FriendshipRequest.objects.filter(pk=pk, to_user=request.user).first()
        if not fr:
            messages.error(request, "Friend request not found.")
            return redirect("users:friend_requests")

        if action == "accept":
            fr.accept()
            messages.success(
                request, f"You are now friends with {fr.from_user.username}."
            )
        elif action == "reject":
            fr.reject()
            messages.info(request, "Friend request rejected.")
        elif action == "cancel" and fr.from_user == request.user:
            fr.cancel()
            messages.info(request, "Friend request cancelled.")
        else:
            messages.error(request, "Invalid action.")

        return redirect("users:friend_requests")


class FriendRequestsListView(LoginRequiredMixin, View):
    def get(self, request):
        from users.models import FriendshipRequest

        received = FriendshipRequest.objects.filter(
            to_user=request.user, status=FriendshipRequest.STATUS_PENDING
        )
        sent = FriendshipRequest.objects.filter(
            from_user=request.user, status=FriendshipRequest.STATUS_PENDING
        )
        return render(
            request, "users/friend_requests.html", {"received": received, "sent": sent}
        )


class FriendsListView(LoginRequiredMixin, View):
    def get(self, request):
        # Use helper on user model
        friends_qs = request.user.friends()
        # For convenience also show mutual friends count etc later
        return render(request, "users/friends_list.html", {"friends": friends_qs})


class PeopleListView(LoginRequiredMixin, View):
    """List all users (except current) with friendship status info."""
    def get(self, request):
        from users.models import FriendshipRequest

        users_qs = get_user_model().objects.exclude(pk=request.user.pk)

        sent = FriendshipRequest.objects.filter(from_user=request.user)
        received = FriendshipRequest.objects.filter(to_user=request.user)

        sent_map = {fr.to_user.pk: fr for fr in sent}
        received_map = {fr.from_user.pk: fr for fr in received}
        friends_ids = set(request.user.friends().values_list('id', flat=True))

        people = []
        for u in users_qs:
            entry = {"user": u, "status": "none", "request_pk": None}
            if u.pk in friends_ids:
                entry["status"] = "friends"
            elif u.pk in sent_map:
                entry["status"] = "sent"
                entry["request_pk"] = sent_map[u.pk].pk
            elif u.pk in received_map:
                entry["status"] = "received"
                entry["request_pk"] = received_map[u.pk].pk
            people.append(entry)

        return render(request, 'users/people.html', {
            'people': people,
        })


class UserProfileView(LoginRequiredMixin, View):
    """View another user's profile and show friendship actions."""
    def get(self, request, pk):
        from users.models import FriendshipRequest

        target = get_object_or_404(get_user_model(), pk=pk)
        # Determine relationship
        fr_sent = FriendshipRequest.objects.filter(from_user=request.user, to_user=target).first()
        fr_received = FriendshipRequest.objects.filter(from_user=target, to_user=request.user).first()
        is_friend = request.user.is_friend_with(target)

        return render(request, 'users/user_profile.html', {
            'target': target,
            'fr_sent': fr_sent,
            'fr_received': fr_received,
            'is_friend': is_friend,
        })
