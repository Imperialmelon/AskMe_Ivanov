
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'AskMe'
urlpatterns = [
    path('', views.questions_list, name='question_list'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.register, name='register'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('settings/', views.settings, name='settings'),
    path('hot/', views.hot_questions, name='hot_questions'),  # Move this before the tag pattern
    path('<str:tag_name>/', views.questions_with_tag, name='get_by_tag'),  # This should be last
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)