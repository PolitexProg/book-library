from django.shortcuts import render
from app.models import BookReview
# Create your views here.


def landing_page(request):
    return render(request, "landing.html")


def home_page(request):
    book_reviews = (
        BookReview.objects.select_related("book", "user").all().order_by("-created_at")
    )
    return render(request, "home.html", {"book_reviews": book_reviews})
