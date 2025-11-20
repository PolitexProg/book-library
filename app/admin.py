from django.contrib import admin
from app.models import Book, Author, BookAuthor, BookReview


# --- INLINES ---
class BookAuthorInline(admin.TabularInline):
    """Позволяет управлять связью Автор-Книга на странице Книги."""

    model = BookAuthor
    extra = 1


class BookReviewInline(admin.TabularInline):
    """Позволяет просматривать и управлять рецензиями на странице Книги."""

    model = BookReview
    readonly_fields = ("user", "stars_given")
    can_delete = False
    max_num = 0


# --- ADMIN MODELS ---


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Настройка отображения модели Книга."""

    list_display = ("title", "isbn")
    search_fields = ("title", "isbn")
    list_display_links = ("title",)
    inlines = [
        BookAuthorInline,
        BookReviewInline,
    ]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Настройка отображения модели Автор."""

    list_display = ("first_name", "last_name", "email")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("last_name",)


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    """Настройка отображения модели Рецензия."""

    list_display = ("book", "user", "stars_given")
    list_filter = ("stars_given",)
    list_select_related = ("user", "book")
    search_fields = ("content", "user__username", "book__title")
