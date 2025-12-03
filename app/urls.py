from django.urls import path
from app.views import AddBookReviewView, BookDetailView, BooksView, add_to_wishlist, remove_from_wishlist, WishlistView

app_name = "books"

urlpatterns = [
    path("", BooksView.as_view(), name="list"),
    path("<int:pk>/", BookDetailView.as_view(), name="detail"),
    path("<int:pk>/review/", AddBookReviewView.as_view(), name="add_review"),
    path("<int:book_id>/add_to_wishlist/", add_to_wishlist, name="add_to_wishlist"),
    path("<int:book_id>/remove_from_wishlist/", remove_from_wishlist, name="remove_from_wishlist"),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),

]
