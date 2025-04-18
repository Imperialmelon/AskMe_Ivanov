from typing import Any
from django import forms
from django.contrib.auth.models import User
from .models import Question, Answer, Profile, Tag
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(
            attrs={"class": "form-control w-50", "placeholder": "Enter your nickname"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control w-50", "placeholder": "Enter your password"}
        ),
    )


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Passowrd", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeat passowrd", widget=forms.PasswordInput)
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={"class": "form-control-file", "accept": "image/*"}
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your nickname",
                    "minlength": 5,
                    "maxlength": 25,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email",
                }
            ),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your password",
                "minlength": 8,
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Confirm your password",
                "minlength": 8,
            }
        )

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email

    def clean_password2(self) -> str:
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 and password2 and password2 != password1:
            raise ValidationError("Passwords dont match")
        return password2

    def save(self) -> User:
        user = get_user_model().objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
        )
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            Profile.objects.create(user=user, avatar=avatar)
        else:
            Profile.objects.create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label="Login",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your new username",
                "minlength": "3",
                "maxlength": "50",
            }
        ),
        min_length=3,
        max_length=50,
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your new email"}
        ),
    )
    avatar = forms.ImageField(
        label="Avatar",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control-file"}),
    )

    class Meta:
        model = Profile
        fields = ["avatar"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields["email"].initial = self.user.email
            self.fields["username"].initial = self.user.username
            if hasattr(self.user, "profile"):
                self.instance = self.user.profile

    def clean_username(self) -> str:
        username = self.cleaned_data.get("username").strip()
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise ValidationError("User with that username already exists.")
        return username

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email").strip()
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("User with that email already exists.")
        return email

    def save(self, commit: bool = True) -> Profile:
        profile = super().save(commit=False)
        user = self.user

        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]

        if "avatar" in self.cleaned_data and self.cleaned_data["avatar"] is not None:
            profile.avatar = self.cleaned_data["avatar"]

        if commit:
            user.save()
            profile.save()

        return profile


class AskForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter question title"}
        ),
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Your question",
                "rows": "10",
                "cols": "50",
            }
        ),
        required=True,
    )
    tags = forms.CharField(
        help_text="Enter tags, separated by commas.",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your tags"}
        ),
    )

    class Meta:
        model = Question
        fields = ["title", "content", "tags"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_content(self) -> str:
        content = self.cleaned_data.get("content")
        if len(content) == 0:
            raise ValidationError("Content cant be empty")
        return content

    def clean_tags(self) -> list[str]:
        tags = self.cleaned_data.get("tags")
        print(tags)
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if not tags_list:
                raise ValidationError("No valid tags provided")
            return tags_list
        return []

    def save(self, commit: bool = True) -> Question:
        question = Question(
            author=self.user,
            title=self.cleaned_data["title"],
            content=self.cleaned_data["content"],
        )
        if commit:
            question.save()
            tags = set(self.cleaned_data.get("tags", []))
            print(tags)
            for tag_name in tags:
                tag, created = Tag.objects.get_or_create(title=tag_name.lower())
                question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    content = forms.CharField(
        label="Answer",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Leave your answer here",
                "rows": "5",
            }
        ),
        required=True,
    )

    class Meta:
        model = Answer
        fields = ["content"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        self.question_id = kwargs.pop("question_id", None)
        super().__init__(*args, **kwargs)

    def clean_content(self) -> str:
        content = self.cleaned_data["content"]
        if len(content) == 0:
            raise ValidationError("Answer cant be empty")
        return content

    def save(self, commit: bool = True) -> Answer:
        question = Question.objects.get(pk=self.question_id)
        answer = Answer(
            author=self.user, question=question, content=self.cleaned_data["content"]
        )
        if commit:
            question.save()
            answer.save()
        return answer
