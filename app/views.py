from django.views.generic import ListView, DetailView
from django.db.models import Q, Avg, Count
from app.models import Book, BookAuthor, BookReview, WishListItem
from django.core.paginator import Paginator
from app.forms import BookDetailReviewForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.http import Http404
from users.models import CustomUser
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Book, WishListItem
from notifications.models import Notification


class BooksView(ListView):
    template_name = "books/list.html"
    context_object_name = "books"
    paginate_by = 2

    def get_queryset(self):
        """Return a queryset optionally filtered by a search query.

        Supports searching by title, description, isbn and author name. Also
        orders the queryset by title to make pagination deterministic.
        """
        qs = Book.objects.all().order_by("title")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(isbn__icontains=q)
                | Q(bookauthor__author__first_name__icontains=q)
                | Q(bookauthor__author__last_name__icontains=q)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        """Add the search query to context so templates can prefill the search box
        and include the query in pagination links.
        """
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class BookDetailView(DetailView):
    template_name = "books/detail.html"
    model = Book
    context_object_name = "book"
    form_class = BookDetailReviewForm

    def get_queryset(self):
        return super().get_queryset().annotate(
            average_rating=Avg("bookreview__stars_given"),
            review_count=Count("bookreview")
        )

    def get_context_data(self, **kwargs):
        """Add related authors and reviews to the context."""
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        context["authors"] = BookAuthor.objects.filter(book=book).select_related(
            "author"
        )
        context["reviews"] = BookReview.objects.filter(book=book).select_related("user")
        context["review_form"] = self.form_class()
        
        # Check if book is in user's wishlist
        if self.request.user.is_authenticated:
            context["is_in_wishlist"] = WishListItem.objects.filter(
                user=self.request.user, book=book
            ).exists()
        else:
            context["is_in_wishlist"] = False
            
        return context


class AddBookReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(
            Book.objects.annotate(
                average_rating=Avg("bookreview__stars_given"),
                review_count=Count("bookreview")
            ),
            pk=pk
        )
        form = BookDetailReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            try:
                with transaction.atomic():
                    review.save()
                messages.success(request, "Your review has been posted!")
                return redirect("books:detail", pk=book.pk)
            except IntegrityError:
                messages.error(
                    request,
                    "You have already reviewed this book. You can only review each book once.",
                )

        context = {
            "book": book,
            "authors": BookAuthor.objects.filter(book=book).select_related("author"),
            "reviews": BookReview.objects.filter(book=book).select_related("user"),
            "review_form": form,
        }
        return render(request, "books/detail.html", context)


class TeachersDashboardView(LoginRequiredMixin, ListView):
    template_name = "books/teachers_dashboard.html"
    model = Book
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role != "teacher":
            raise Http404("You are not authorized to view this page.")
        teacher_class = user.school_class

        students = CustomUser.objects.filter(role="student", school_class=teacher_class)
        reviews = BookReview.objects.filter(user__in=students)

        books_stats = (
            reviews.values("book", "book__title", "book__cover_picture")
            .annotate(
                avg_rating=Avg("stars_given"),
                review_count=Count("id")
            )
            .order_by("-avg_rating")[:5]
        )

        context["books_stats"] = books_stats
        context["class_name"] = teacher_class
        return context

@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    WishListItem.objects.get_or_create(user=request.user, book=book)
    messages.success(request, f'"{book.title}" has been added to your wishlist.')
    Notification.objects.create(user=request.user, message=f'"{book.title}" has been added to your wishlist.')
    return redirect("books:detail", pk=book_id)

@login_required
def remove_from_wishlist(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    WishListItem.objects.filter(user=request.user, book=book).delete()
    messages.info(request, f'"{book.title}" has been removed from your wishlist.')
    return redirect("books:detail", pk=book_id)

class WishlistView(LoginRequiredMixin, ListView):
    template_name = "books/wishlist.html"
    context_object_name = "wishlist_books"

    def get_queryset(self):
        return Book.objects.filter(wishlist_items__user=self.request.user)