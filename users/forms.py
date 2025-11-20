from typing import Any
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserCreateForm(forms.ModelForm):
    password2 = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput, strip=False
    )
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, strip=False
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError(
                "Пароли не совпадают. Пожалуйста, введите их повторно."
            )
        return cleaned_data

    def save(self, commit: bool = True) -> Any:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "profile_picture")
