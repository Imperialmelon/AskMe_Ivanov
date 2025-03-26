from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

tags = ['Redis', 'Django', 'Kafka', 'FastApi', 'PostgeSQL', 'MYSQL', 'C#', 'Python', 'C++', 'Go', 'HTML', 'CSS', 'React', 'Redux',
        'Tauri', 'ORM', 'Alchemy', 'AioHttp', 'REST', 'Kotlin', 'Swift', 'Vue', 'Angular', 'Java', 'JavaScript', 'TypeScript', 'Spring', 'Shrek']


from random import randrange, randint, choice




question_mocks = [
        {'id' : i, 'likes' : randrange(i+10), 'title' : 'Why is my Next.js + Spring Boot website running slow on a VPS, and how can I fix it?', 'text' : ' I am working on a project similar to prompthero.com, where users can post AI-generated images along with their prompts.',
         'tags' : [tags[randint(0,len(tags) - 1)] for _ in range(3)], 'answers' : randint(0,23)} for i in range(22)
    ]

ans_texts = ['kill yourself plz', 'just google it lmao', 'you are stupid', 'try to rerun the code', 'хз чел', 'иди документацию читай']


class User:
        login = 'Name'
        email = 'aboba@yandex.ru'
        password = 'password'
        nickname = 'Name'
        pic = 'img\no_avatar.jpg'
user = User()

answers_mocks = [
    {
        'id' : i, 'text' : choice(ans_texts), 'question_id' : choice(range(len(question_mocks))), 'author' : user, 'likes' : randrange(1,20)
    } for i in range(300)
]



def questions_list(request):
    question_title = request.GET.get('question_title')
    if question_title:
        questions = [question for question in question_mocks if question['title'] in question_title]
        questions = paginate(request, questions)
    else:
        questions = paginate(request, question_mocks)
    return render(
        request,
        'askme/questions/index.html',
        {
            'is_auth' : True,
            'questions' : questions
        }
    )

def paginate(request, objects, per_page=5):
    paginator = Paginator(objects, per_page)  
    page = request.GET.get('page', 1)
    
    try:
        paginated_objects = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        paginated_objects = paginator.page(1)
 
    return paginated_objects


def login(request):
    return render(
        request,
        'askme/user/login.html',
        {'is_auth' : False,
        'user' : user}
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
    # print(question_id)
    # print(question_id)
    answers = [answer for answer in answers_mocks if answer['question_id'] == question_id]
    answers = paginate(request, answers, 3)

    question = question_mocks[question_id]
    return render(
        request,
        'askme/questions/question.html',
        {'is_auth' : True,
         'question' : question,
         'answers' : answers,
         'user' : user
         }

    )


def questions_with_tag(request, tag):
    print(tag)
    if tag is {}:
        print(1)
        tag = tag['tag']
    print(tag)
    questions = [q for q in question_mocks if tag in q['tags']]
    questions = paginate(request, questions, 5)
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
         'user' : user}
    )

def hot_questions(request):
    question_answer_counts = {}
    for question in question_mocks:
        question_id = question['id']
        question_answer_counts[question_id] = 0

    for answer in answers_mocks:
        question_id = answer['question_id']
        if question_id in question_answer_counts:
            question_answer_counts[question_id] += 1

    sorted_question_mocks = sorted(question_mocks, key=lambda question: question_answer_counts[question['id']], reverse=True)
    return render(
        request, 
        'askme/questions/hot.html',
        {'is_auth' : True,
         'questions' : sorted_question_mocks[:10]

         }
    )