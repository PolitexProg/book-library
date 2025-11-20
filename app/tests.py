from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from app.models import Book, Author, BookAuthor, BookReview
from app.forms import BookDetailReviewForm

User = get_user_model()


# ==================== Book Model Tests ====================
class BookModelTests(TestCase):
    """Test cases for the Book model."""

    def setUp(self):
        """Set up test data."""
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book description",
            isbn="978-0-1234-5678-9",
        )

    def test_book_creation(self):
        """Test that a book can be created successfully."""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.description, "A test book description")
        self.assertEqual(self.book.isbn, "978-0-1234-5678-9")

    def test_book_str_representation(self):
        """Test the string representation of a Book."""
        self.assertEqual(str(self.book), "Test Book")

    def test_book_isbn_unique(self):
        """Test that ISBN must be unique."""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Another Book",
                description="Another test book",
                isbn="978-0-1234-5678-9",  # Same ISBN as self.book
            )

    def test_book_title_max_length(self):
        """Test that book title cannot exceed 200 characters."""
        long_title = "a" * 201
        book = Book(title=long_title, description="Test", isbn="978-0-1234-5678-0")
        with self.assertRaises(Exception):
            book.full_clean()

    def test_book_isbn_max_length(self):
        """Test that ISBN cannot exceed 17 characters."""
        long_isbn = "a" * 18
        book = Book(title="Test", description="Test", isbn=long_isbn)
        with self.assertRaises(Exception):
            book.full_clean()

    def test_book_cover_picture_optional(self):
        """Test that cover_picture is optional."""
        book = Book.objects.create(
            title="Book Without Cover",
            description="A book without a cover",
            isbn="978-0-1234-5678-1",
        )
        self.assertIsNotNone(book.cover_picture)  # Should have default

    def test_book_default_cover(self):
        """Test that a book without cover gets default cover."""
        self.assertIn("default_cover", self.book.cover_picture.name)

    def test_book_verbose_names(self):
        """Test model Meta verbose names."""
        self.assertEqual(Book._meta.verbose_name, "Book")
        self.assertEqual(Book._meta.verbose_name_plural, "Books")


# ==================== Author Model Tests ====================
class AuthorModelTests(TestCase):
    """Test cases for the Author model."""

    def setUp(self):
        """Set up test data."""
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            bio="A talented author",
        )

    def test_author_creation(self):
        """Test that an author can be created successfully."""
        self.assertEqual(self.author.first_name, "John")
        self.assertEqual(self.author.last_name, "Doe")
        self.assertEqual(self.author.email, "john@example.com")

    def test_author_str_representation(self):
        """Test the string representation of an Author."""
        self.assertEqual(str(self.author), "John Doe")

    def test_author_email_optional(self):
        """Test that email is optional."""
        author = Author.objects.create(first_name="Jane", last_name="Smith")
        self.assertIsNone(author.email)

    def test_author_bio_optional(self):
        """Test that bio is optional."""
        author = Author.objects.create(first_name="Jane", last_name="Smith")
        self.assertIsNone(author.bio)

    def test_author_ordering(self):
        """Test that authors are ordered by last_name, then first_name."""
        # Ensure a clean set for deterministic ordering
        Author.objects.all().delete()
        Author.objects.create(first_name="Bob", last_name="Alpha")
        Author.objects.create(first_name="Charlie", last_name="Alpha")
        Author.objects.create(first_name="Alice", last_name="Zeta")

        authors = list(Author.objects.all())
        # Expected order: Alpha (Bob), Alpha (Charlie), Zeta (Alice)
        self.assertEqual(authors[0].last_name, "Alpha")
        self.assertEqual(authors[0].first_name, "Bob")
        self.assertEqual(authors[1].first_name, "Charlie")
        self.assertEqual(authors[2].last_name, "Zeta")

    def test_author_verbose_names(self):
        """Test model Meta verbose names."""
        self.assertEqual(Author._meta.verbose_name, "Author")
        self.assertEqual(Author._meta.verbose_name_plural, "Authors")


# ==================== BookAuthor Model Tests ====================
class BookAuthorModelTests(TestCase):
    """Test cases for the BookAuthor model (many-to-many relationship)."""

    def setUp(self):
        """Set up test data."""
        self.book = Book.objects.create(
            title="Python Guide",
            description="A comprehensive guide",
            isbn="978-0-5678-1234-5",
        )
        self.author = Author.objects.create(first_name="Guido", last_name="Van Rossum")

    def test_book_author_creation(self):
        """Test that a BookAuthor relationship can be created."""
        book_author = BookAuthor.objects.create(book=self.book, author=self.author)
        self.assertEqual(book_author.book, self.book)
        self.assertEqual(book_author.author, self.author)

    def test_book_author_cascade_delete_book(self):
        """Test that deleting a book cascades to BookAuthor."""
        BookAuthor.objects.create(book=self.book, author=self.author)
        self.assertEqual(BookAuthor.objects.count(), 1)

        self.book.delete()
        self.assertEqual(BookAuthor.objects.count(), 0)

    def test_book_author_cascade_delete_author(self):
        """Test that deleting an author cascades to BookAuthor."""
        BookAuthor.objects.create(book=self.book, author=self.author)
        self.assertEqual(BookAuthor.objects.count(), 1)

        self.author.delete()
        self.assertEqual(BookAuthor.objects.count(), 0)

    def test_multiple_authors_per_book(self):
        """Test that a book can have multiple authors."""
        author2 = Author.objects.create(first_name="Raymond", last_name="Hettinger")
        BookAuthor.objects.create(book=self.book, author=self.author)
        BookAuthor.objects.create(book=self.book, author=author2)

        book_authors = BookAuthor.objects.filter(book=self.book)
        self.assertEqual(book_authors.count(), 2)

    def test_author_multiple_books(self):
        """Test that an author can have multiple books."""
        book2 = Book.objects.create(
            title="Advanced Python",
            description="Advanced concepts",
            isbn="978-0-9876-5432-1",
        )
        BookAuthor.objects.create(book=self.book, author=self.author)
        BookAuthor.objects.create(book=book2, author=self.author)

        author_books = BookAuthor.objects.filter(author=self.author)
        self.assertEqual(author_books.count(), 2)


# ==================== BookReview Model Tests ====================
class BookReviewModelTests(TestCase):
    """Test cases for the BookReview model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="reviewer", email="reviewer@example.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Amazing Book", description="A great read", isbn="978-0-1111-2222-3"
        )

    def test_book_review_creation(self):
        """Test that a book review can be created."""
        review = BookReview.objects.create(
            user=self.user,
            book=self.book,
            content="This is an amazing book!",
            stars_given=5,
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.book, self.book)
        self.assertEqual(review.stars_given, 5)

    def test_book_review_stars_range(self):
        """Test that stars_given must be between 1 and 5."""
        # Invalid: 0 stars
        review_low = BookReview(
            user=self.user, book=self.book, content="Bad", stars_given=0
        )
        with self.assertRaises(ValidationError):
            review_low.full_clean()

        # Invalid: 6 stars
        review_high = BookReview(
            user=self.user, book=self.book, content="Too good", stars_given=6
        )
        with self.assertRaises(ValidationError):
            review_high.full_clean()

    def test_book_review_stars_min_valid(self):
        """Test that 1 star is the minimum valid rating."""
        review = BookReview.objects.create(
            user=self.user, book=self.book, content="Not great", stars_given=1
        )
        self.assertEqual(review.stars_given, 1)

    def test_book_review_stars_max_valid(self):
        """Test that 5 stars is the maximum valid rating."""
        review = BookReview.objects.create(
            user=self.user, book=self.book, content="Perfect!", stars_given=5
        )
        self.assertEqual(review.stars_given, 5)

    def test_book_review_unique_per_user_book(self):
        """Test that a user can only review a book once."""
        BookReview.objects.create(
            user=self.user, book=self.book, content="First review", stars_given=4
        )

        # Attempting to create a second review should fail
        with self.assertRaises(Exception):
            BookReview.objects.create(
                user=self.user, book=self.book, content="Second review", stars_given=5
            )

    def test_book_review_str_representation(self):
        """Test the string representation of a BookReview."""
        review = BookReview.objects.create(
            user=self.user, book=self.book, content="Great book!", stars_given=4
        )
        expected_str = f"Review reviewer to Amazing Book"
        self.assertEqual(str(review), expected_str)

    def test_book_review_cascade_delete_user(self):
        """Test that deleting a user cascades to their reviews."""
        BookReview.objects.create(
            user=self.user, book=self.book, content="Good", stars_given=4
        )
        self.assertEqual(BookReview.objects.count(), 1)

        self.user.delete()
        self.assertEqual(BookReview.objects.count(), 0)

    def test_book_review_cascade_delete_book(self):
        """Test that deleting a book cascades to its reviews."""
        BookReview.objects.create(
            user=self.user, book=self.book, content="Good", stars_given=4
        )
        self.assertEqual(BookReview.objects.count(), 1)

        self.book.delete()
        self.assertEqual(BookReview.objects.count(), 0)


# ==================== Books View Tests ====================
class BooksListViewTests(TestCase):
    """Test cases for the BooksView (list view)."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        # Create multiple books for pagination testing
        for i in range(5):
            Book.objects.create(
                title=f"Book {i + 1}",
                description=f"Description for book {i + 1}",
                isbn=f"978-0-{i:04d}-5678-{i}",
            )

    def test_books_list_view_accessible(self):
        """Test that the books list view is accessible."""
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)

    def test_books_list_view_uses_correct_template(self):
        """Test that the books list view uses the correct template."""
        response = self.client.get(reverse("books:list"))
        self.assertTemplateUsed(response, "books/list.html")

    def test_books_list_view_context(self):
        """Test that the context contains books."""
        response = self.client.get(reverse("books:list"))
        self.assertIn("books", response.context)

    def test_books_list_pagination(self):
        """Test that pagination works correctly (paginate_by=2)."""
        response = self.client.get(reverse("books:list"))
        # First page should have 2 books
        self.assertEqual(len(response.context["books"]), 2)

    def test_books_list_second_page_pagination(self):
        """Test pagination on second page."""
        response = self.client.get(reverse("books:list") + "?page=2")
        # Second page should have 2 books
        self.assertEqual(len(response.context["books"]), 2)

    def test_books_list_third_page_pagination(self):
        """Test pagination on third page."""
        response = self.client.get(reverse("books:list") + "?page=3")
        # Third page should have 1 book (5 total, 2 per page)
        self.assertEqual(len(response.context["books"]), 1)

    def test_books_list_invalid_page(self):
        """Test that an invalid page number returns 404."""
        response = self.client.get(reverse("books:list") + "?page=999")
        self.assertEqual(response.status_code, 404)

    def test_books_list_no_books(self):
        """Test the list view when no books exist."""
        Book.objects.all().delete()
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 0)

    def test_books_list_content_type(self):
        """Test that the response is HTML."""
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")


# ==================== Book Detail View Tests ====================
class BookDetailViewTests(TestCase):
    """Test cases for the BookDetailView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.book = Book.objects.create(
            title="Python Mastery",
            description="Learn Python the right way",
            isbn="978-0-7890-1234-5",
        )

    def test_book_detail_view_accessible(self):
        """Test that the book detail view is accessible."""
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)

    def test_book_detail_view_uses_correct_template(self):
        """Test that the detail view uses the correct template."""
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertTemplateUsed(response, "books/detail.html")

    def test_book_detail_view_context(self):
        """Test that the context contains the book object."""
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertIn("book", response.context)
        self.assertEqual(response.context["book"], self.book)

    def test_book_detail_view_book_data(self):
        """Test that the detail view displays correct book data."""
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book.description)
        self.assertContains(response, self.book.isbn)

    def test_book_detail_view_nonexistent_book(self):
        """Test that accessing a nonexistent book returns 404."""
        response = self.client.get(reverse("books:detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_book_detail_view_content_type(self):
        """Test that the response is HTML."""
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")


# ==================== Book Review Form Tests ====================
class BookDetailReviewFormTests(TestCase):
    """Test cases for the BookDetailReviewForm."""

    def setUp(self):
        """Set up test data."""
        self.book = Book.objects.create(
            title="Reviewable Book",
            description="A book for testing reviews",
            isbn="978-0-9999-9999-9",
        )

    def test_review_form_valid(self):
        """Test that a valid review form can be created."""
        form_data = {"content": "This is a great book!", "stars_given": 5}
        form = BookDetailReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_missing_content(self):
        """Test that review form requires content."""
        form_data = {"content": "", "stars_given": 5}
        form = BookDetailReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_review_form_missing_stars(self):
        """Test that review form requires stars_given."""
        form_data = {"content": "Good book", "stars_given": ""}
        form = BookDetailReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("stars_given", form.errors)

    def test_review_form_invalid_star_rating_zero(self):
        """Test that 0 stars is invalid."""
        form_data = {"content": "Bad book", "stars_given": 0}
        form = BookDetailReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_review_form_invalid_star_rating_high(self):
        """Test that 6 stars is invalid."""
        form_data = {"content": "Too good", "stars_given": 6}
        form = BookDetailReviewForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_review_form_valid_min_stars(self):
        """Test that 1 star is valid."""
        form_data = {"content": "Not great", "stars_given": 1}
        form = BookDetailReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_valid_max_stars(self):
        """Test that 5 stars is valid."""
        form_data = {"content": "Perfect!", "stars_given": 5}
        form = BookDetailReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_save_creates_review_object(self):
        """Test that saving the form creates a BookReview instance."""
        form_data = {"content": "Excellent read", "stars_given": 4}
        form = BookDetailReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        review = form.save(commit=False)
        self.assertIsInstance(review, BookReview)
        self.assertEqual(review.content, "Excellent read")
        self.assertEqual(review.stars_given, 4)


# ==================== Add Book Review View Tests ====================
class AddBookReviewViewTests(TestCase):
    """Test cases for the AddBookReviewView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="reviewer", email="reviewer@example.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Review Test Book",
            description="A book for testing reviews",
            isbn="978-0-8888-8888-8",
        )

    def test_add_review_requires_login(self):
        """Test that adding a review requires login."""
        response = self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Great book", "stars_given": 5},
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn("/users/login", response["Location"])

    def test_add_review_authenticated_user(self):
        """Test that an authenticated user can add a review."""
        self.client.login(username="reviewer", password="testpass123")
        response = self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Amazing book!", "stars_given": 5},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        # Check that review was created
        self.assertTrue(
            BookReview.objects.filter(
                user=self.user, book=self.book, stars_given=5
            ).exists()
        )

    def test_add_review_creates_review_object(self):
        """Test that adding a review creates a BookReview instance."""
        self.client.login(username="reviewer", password="testpass123")
        self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Loved it!", "stars_given": 5},
        )
        review = BookReview.objects.get(user=self.user, book=self.book)
        self.assertEqual(review.content, "Loved it!")
        self.assertEqual(review.stars_given, 5)

    def test_add_review_nonexistent_book(self):
        """Test that adding a review to a nonexistent book returns 404."""
        self.client.login(username="reviewer", password="testpass123")
        response = self.client.post(
            reverse("books:add_review", args=[9999]),
            data={"content": "Great", "stars_given": 4},
        )
        self.assertEqual(response.status_code, 404)

    def test_add_review_invalid_data(self):
        """Test that invalid review data doesn't create a review."""
        self.client.login(username="reviewer", password="testpass123")
        response = self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "", "stars_given": 5},  # Missing content
            follow=True,
        )
        self.assertFalse(
            BookReview.objects.filter(user=self.user, book=self.book).exists()
        )

    def test_add_review_redirects_to_detail(self):
        """Test that after adding a review, user is redirected to book detail."""
        self.client.login(username="reviewer", password="testpass123")
        response = self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Good", "stars_given": 4},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("books:detail", args=[self.book.pk]), response["Location"]
        )

    def test_add_review_unique_per_user_book(self):
        """Test that a user cannot add multiple reviews to the same book."""
        self.client.login(username="reviewer", password="testpass123")
        # Add first review
        response1 = self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Good book", "stars_given": 4},
        )
        self.assertEqual(response1.status_code, 302)  # Success redirect

        # Attempt to add second review
        response2 = self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Different review", "stars_given": 3},
            follow=True,
        )
        # Should re-render detail page with error message
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, "already reviewed")

        # Check that only one review exists
        self.assertEqual(
            BookReview.objects.filter(user=self.user, book=self.book).count(), 1
        )

    def test_add_review_multiple_users(self):
        """Test that multiple users can review the same book."""
        user2 = User.objects.create_user(
            username="reviewer2", email="reviewer2@example.com", password="testpass123"
        )
        # First user adds review
        self.client.login(username="reviewer", password="testpass123")
        self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Great book", "stars_given": 5},
        )
        self.client.logout()

        # Second user adds review
        self.client.login(username="reviewer2", password="testpass123")
        self.client.post(
            reverse("books:add_review", args=[self.book.pk]),
            data={"content": "Good book", "stars_given": 4},
        )

        # Check that two reviews exist
        self.assertEqual(BookReview.objects.filter(book=self.book).count(), 2)

    def test_book_detail_view_includes_review_form(self):
        """Test that book detail view includes the review form in context."""
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertIn("review_form", response.context)
        self.assertIsInstance(response.context["review_form"], BookDetailReviewForm)

    def test_book_detail_view_includes_reviews(self):
        """Test that book detail view includes reviews in context."""
        # Create a review
        review = BookReview.objects.create(
            user=self.user, book=self.book, content="Test review", stars_given=4
        )
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertIn("reviews", response.context)
        self.assertIn(review, response.context["reviews"])

    def test_book_detail_view_displays_reviews(self):
        """Test that book detail view displays reviews on the page."""
        review = BookReview.objects.create(
            user=self.user, book=self.book, content="Excellent read", stars_given=5
        )
        response = self.client.get(reverse("books:detail", args=[self.book.pk]))
        self.assertContains(response, review.user.username)
        self.assertContains(response, "Excellent read")
