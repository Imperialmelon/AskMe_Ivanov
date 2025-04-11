
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from random import randrange, randint, choice
from .models import Question

from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404

from .models import Question, Tag, Profile, Answer
from .utils import paginate
from .forms import *
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
# SINGLETON_USER = User(id=1001, username='student', email = 'email@yandex.ru', first_name = 'Name')
from django.contrib.auth.decorators import login_required

def questions_list(request):
    print(request.user)

    question_title = request.GET.get('question_title', '')
    questions = Question.objects.new().filter(title__icontains=question_title)
    questions = paginate(request, questions)
    print(question_title)
    return render(
        request,
        'askme/questions/index.html',
        {
            'is_auth' : False,
            'questions' : questions
        }
    )



def login(request):
    if request.user.is_authenticated:
         return redirect(request.GET.get('next') or request.GET.get('continue', '/'))
    
    form = LoginForm()
    print(request.POST)
    if request.method == 'POST':
        form = LoginForm(data = request.POST)
        if form.is_valid():

            user = authenticate(request, username = form.cleaned_data['username'], password = form.cleaned_data['password'])
            print(form.cleaned_data)
            if user:
                print('got')
                django_login(request, user)
                return redirect(request.GET.get('next') or request.GET.get('continue', '/'))
            form.add_error(None, 'Incorrect username or password')
    return render(
        request,
        'askme/user/login.html',
        {'form' : form}
    )

login_required
def logout(request):
    print(1)
    django_logout(request)
    return redirect('/')


def register(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get('next') or request.GET.get('continue', 'index'))
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            if user:
                django_login(request, user)
                return redirect('/')


    return render(
        request,
        'askme/user/signup.html',
        {'form' : form}
    )


@login_required
def ask(request):
    form = AskForm(user=request.user)
    print(request.POST)
    if request.method == 'POST':
        form = AskForm(request.POST, user=request.user)
 
        if form.is_valid():
            question = form.save()
            return redirect('AskMe:question_detail', question_id=question.pk)


    return render(
        request,
        'askme/questions/ask.html',
        {'form' : form}
    )

def question_detail(request, question_id):

    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.get_answers(question_id)
    answers = paginate(request, answers)
    form = AnswerForm(question_id=question_id, user=request.user)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/login/')
        form = AnswerForm(request.POST, question_id=question_id, user=request.user)
        if form.is_valid():
            answer = form.save()
            return redirect(reverse('AskMe:question_detail', args=[question_id]))
    return render(
        request,
        'askme/questions/question.html',
        {'form' : form,
         'question' : question,
         'answers' : answers,
         }

    )


def questions_with_tag(request, tag_name):
    tag = get_object_or_404(Tag, title=tag_name)
    questions = Question.objects.tagged(tag.title)
    questions = paginate(request, questions)
    print(tag)
    return render(
        request,
        'askme/questions/tag.html',
        {'is_auth' : True,
         'tag' : tag,
         'questions' : questions
         
         }
    )


@login_required
def settings(request):
    form = ProfileForm(instance=request.user.profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            django_login(request, request.user)
            return redirect('/settings/')
    return render(
        request,
        'askme/user/settings.html',
        {
         'form' : form}
    )

def hot_questions(request):
    questions = Question.objects.hot()
    questions = paginate(request, questions)
    return render(
        request, 
        'askme/questions/hot.html',
        {'is_auth' : True,
         'questions' : questions

         }
    )
