from django.http import Http404, HttpRequest, HttpResponse
from django.urls import reverse
from .models import Question
from django.shortcuts import redirect, render, get_object_or_404

from .models import Tag, Answer, QuestionLike, AnswerLike
from .utils import paginate
from .forms import LoginForm, RegisterForm, AnswerForm, ProfileForm, AskForm
from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Exists, OuterRef


def questions_list(request: HttpRequest) -> HttpResponse:
    question_title = request.GET.get("question_title", "")
    questions = Question.objects.new().filter(title__icontains=question_title)
    if request.user.is_authenticated:
        questions = questions.annotate(
            is_liked=Exists(
                QuestionLike.objects.filter(user=request.user, question=OuterRef("pk"))
            )
        )
    questions = paginate(request, questions)
    return render(
        request,
        "askme/questions/index.html",
        {"questions": questions},
    )


def login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") or request.GET.get("continue", "/"))

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user:
                django_login(request, user)
                return redirect(
                    request.GET.get("next") or request.GET.get("continue", "/")
                )
            form.add_error(None, "Incorrect username or password")
    return render(request, "askme/user/login.html", {"form": form})


@login_required
def logout(request: HttpRequest) -> HttpResponse:
    django_logout(request)
    return redirect("/")


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect(request.GET.get("continue", "/"))
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            if user:
                django_login(request, user)
                return redirect("/")

    return render(request, "askme/user/signup.html", {"form": form})


@login_required
def ask(request: HttpRequest) -> HttpResponse:
    form = AskForm(user=request.user)
    if request.method == "POST":
        form = AskForm(request.POST, user=request.user)

        if form.is_valid():
            question = form.save()
            return redirect("AskMe:question_detail", question_id=question.pk)

    return render(request, "askme/questions/ask.html", {"form": form})


def question_detail(request: HttpRequest, question_id: int) -> HttpResponse:
    if request.user.is_authenticated:
        question = (
            Question.objects.filter(id=question_id)
            .annotate(
                is_liked=Exists(
                    QuestionLike.objects.filter(
                        user=request.user, question=OuterRef("pk")
                    )
                )
            )
            .first()
        )
        if not question:
            raise Http404("Question does not exist")
    else:
        question = get_object_or_404(Question, id=question_id)
        question.is_liked = False

    answers = Answer.objects.get_answers(question_id)
    if request.user.is_authenticated:
        answers = answers.annotate(
            is_liked=Exists(
                AnswerLike.objects.filter(user=request.user, answer=OuterRef("pk"))
            )
        )
    for answer in answers:
        if answer.helpful:
            answer.useful_class = "useful-answer"
        else:
            answer.useful_class = ""
    answers = paginate(request, answers)
    form = AnswerForm(question_id=question_id, user=request.user)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("/login/")
        form = AnswerForm(request.POST, question_id=question_id, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse("AskMe:question_detail", args=[question_id]))

    return render(
        request,
        "askme/questions/question.html",
        {
            "form": form,
            "question": question,
            "answers": answers,
        },
    )


def questions_with_tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    tag = get_object_or_404(Tag, title=tag_name)
    questions = Question.objects.tagged(tag.title)
    if request.user.is_authenticated:
        questions = questions.annotate(
            is_liked=Exists(
                QuestionLike.objects.filter(user=request.user, question=OuterRef("pk"))
            )
        )
    questions = paginate(request, questions)
    return render(
        request,
        "askme/questions/tag.html",
        {"tag": tag, "questions": questions},
    )


@login_required
def settings(request: HttpRequest) -> HttpResponse:
    form = ProfileForm(instance=request.user.profile, user=request.user)
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            django_login(request, request.user)
            return redirect("/settings/")
    return render(request, "askme/user/settings.html", {"form": form})


def hot_questions(request: HttpRequest) -> HttpRequest:
    questions = Question.objects.hot()
    if request.user.is_authenticated:
        questions = questions.annotate(
            is_liked=Exists(
                QuestionLike.objects.filter(user=request.user, question=OuterRef("pk"))
            )
        )
    questions = paginate(request, questions)
    return render(request, "askme/questions/hot.html", {"questions": questions})


@require_POST
def question_like(request, question_id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    question = get_object_or_404(Question, id=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user, question=question
    )

    if not created:
        like.delete()

    return JsonResponse(
        {"question_likes_count": question.like_count(), "is_liked": created}
    )


@require_POST
def answer_like(request, answer_id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    answer = get_object_or_404(Answer, id=answer_id)
    like, created = AnswerLike.objects.get_or_create(user=request.user, answer=answer)

    if not created:
        like.delete()

    return JsonResponse(
        {"answer_likes_count": answer.like_count(), "is_liked": created}
    )


@require_POST
def set_useful(request: HttpRequest, answer_id: int) -> JsonResponse:
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    answer = get_object_or_404(Answer, id=answer_id)
    question = answer.question

    if question.author != request.user:
        return JsonResponse(
            {"error": "You are not the author of this question"}, status=403
        )

    answer.helpful = not answer.helpful
    answer.save()

    return JsonResponse(
        {
            "is_useful": answer.helpful,
            "answer_id": answer.id,
            "message": f"Answer marked as {'useful' if answer.helpful else 'not useful'}",
        }
    )
