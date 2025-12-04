# config/urls.py
from django.contrib import admin
from django.urls import path, include
from .view import home_page, landing_page
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("home/", home_page, name="home_page"),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls"), name="users"),
    path("books/", include("app.urls"), name="books"),
    path("notifications/", include("notifications.urls")),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
