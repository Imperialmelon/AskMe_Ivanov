
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from random import randrange, randint, choice
from .models import Question

from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from .models import Question, Tag, Profile, Answer
from .utils import paginate



SINGLETON_USER = User(id=1001, username='student', email = 'email@yandex.ru', first_name = 'Name')


def questions_list(request):


    question_title = request.GET.get('question_title', '')
    questions = Question.objects.new().filter(title__icontains=question_title)
    questions = paginate(request, questions)
    print(question_title)
    return render(
        request,
        'askme/questions/index.html',
        {
            'is_auth' : True,
            'questions' : questions
        }
    )



def login(request):
    return render(
        request,
        'askme/user/login.html',
        {'is_auth' : False,
        'user' : SINGLETON_USER}
    )


def register(request):
    return render(
        request,
        'askme/user/signup.html',
        {'is_auth' : False}
    )

def ask(request):
    return render(
        request,
        'askme/questions/ask.html',
        {'is_auth' : True}
    )

def question_detail(request, question_id):

    question = get_object_or_404(Question, id=question_id)
    answers = Answer.objects.get_answers(question_id)
    answers = paginate(request, answers)
    return render(
        request,
        'askme/questions/question.html',
        {'is_auth' : True,
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

def settings(request):
    return render(
        request,
        'askme/user/settings.html',
        {'is_auth' : True,
         'user' : SINGLETON_USER}
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