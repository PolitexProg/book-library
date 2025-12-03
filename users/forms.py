from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserCreateForm(UserCreationForm):
    school_class = forms.CharField(
        label="School Class",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. 9-A"})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label="Role",
        initial="student"
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "school_class", "role")

    def save(self, commit: bool = True) -> Any:
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "profile_picture", "school_class", "role")
        widgets = {
            "school_class": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 9-A"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }