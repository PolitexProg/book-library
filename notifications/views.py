# notifications/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.http import JsonResponse


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "notifications/list.html", {"notifications": notifications})

@login_required
def mark_all_as_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:notifications_list")

@login_required
def unread_notifications_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"count": count})
