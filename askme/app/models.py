from typing import TYPE_CHECKING
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, QuerySet
from django.urls import reverse

if TYPE_CHECKING:
    pass


class QuestionManager(models.Manager):
    def new(self) -> QuerySet["Question"]:
        return self.order_by("-created")

    def hot(self) -> QuerySet["Question"]:
        return self.annotate(likes_=Count("likes")).order_by("-likes_")

    def tagged(self, tag_title) -> QuerySet["Question"]:
        return self.filter(tags__title=tag_title).order_by("-created")

    def all(self) -> QuerySet["Question"]:
        return super().all()


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField("Tag", related_name="question_tags")
    objects = QuestionManager()

    def __str__(self) -> str:
        return self.title

    def like_count(self) -> int:
        return self.likes.count()

    def answer_count(self) -> int:
        return self.answer_question.count()

    def get_absolute_url(self) -> str:
        return reverse("AskMe:question_detail", args=[self.id])

    class Meta:
        db_table = "question"


class TagManager(models.Manager):
    def popular(self) -> QuerySet["Tag"]:
        return self.annotate(questions_=Count("question_tags")).order_by("-questions_")[
            :20
        ]


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True)
    objects = TagManager()

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "tag"


class ProfileManager(models.Manager):
    def top_users(self) -> QuerySet["Profile"]:
        return (
            self.select_related("user")
            .annotate(answer_cnt=Count("user__answers"))
            .order_by("-answer_cnt")[:10]
        )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        blank=True, null=True, upload_to="avatars/", default="default_pic.jpg"
    )
    objects = ProfileManager()

    def __str__(self) -> str:
        return self.user.username

    class Meta:
        db_table = "profile"


class AnswerManager(models.Manager):
    def get_answers(self, question: Question) -> QuerySet["Answer"]:
        return self.filter(question=question).order_by("-created")


class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answer_question"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    helpful = models.BooleanField(default=False)

    objects = AnswerManager()

    def __str__(self) -> str:
        return f"Answer to {self.question.title} {self.author.username}"

    def like_count(self) -> int:
        return self.likes.count()

    class Meta:
        db_table = "answer"


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="likes"
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")
        db_table = "question_like"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="likes")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "answer")
        db_table = "answer_like"
