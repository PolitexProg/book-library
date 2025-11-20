from django import forms
from app.models import BookReview


class BookDetailReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ("content", "stars_given")
