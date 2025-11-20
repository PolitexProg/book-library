from django.urls import path
from users.views import (
    RegisterView,
    LoginView,
    ProfileView,
    LogoutView,
    ProfileUpdateView,
)
from users import views as users_views

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    # Friend system
    path("friends/", users_views.FriendsListView.as_view(), name="friends_list"),
    path(
        "requests/",
        users_views.FriendRequestsListView.as_view(),
        name="friend_requests",
    ),
    path(
        "send-request/<int:pk>/",
        users_views.SendFriendRequestView.as_view(),
        name="send_friend_request",
    ),
    path(
        "respond-request/<int:pk>/<str:action>/",
        users_views.RespondFriendRequestView.as_view(),
        name="respond_friend_request",
    ),
    path("people/", users_views.PeopleListView.as_view(), name="people"),
    path("user/<int:pk>/", users_views.UserProfileView.as_view(), name="user_profile"),
]
