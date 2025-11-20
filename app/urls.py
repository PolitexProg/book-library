from django.urls import path
from app.views import AddBookReviewView, BookDetailView, BooksView

app_name = "books"

urlpatterns = [
    path("", BooksView.as_view(), name="list"),
    path("<int:pk>/", BookDetailView.as_view(), name="detail"),
    path("<int:pk>/review/", AddBookReviewView.as_view(), name="add_review"),
]
