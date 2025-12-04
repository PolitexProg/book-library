# notifications/urls.py
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('api/unread-count/', views.unread_notifications_count, name='unread_notifications_count')
]