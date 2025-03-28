
from django.contrib import admin
from django.urls import path
from . import views


app_name = 'AskMe'
urlpatterns = [
    path('', views.questions_list, name='question_list'),
    path('login/', views.login, name='login'),
    path('signup/', views.register, name='register'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('question/<str:tag_name>/', views.questions_with_tag, name='get_by_tag'),
    path('settings/', views.settings, name='settings'),
    path('hot/', views.hot_questions, name='hot_questions'),
]
