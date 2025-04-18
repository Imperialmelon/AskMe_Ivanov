from django.contrib import admin
from .models import Answer, AnswerLike, Question, QuestionLike, Tag, Profile


# Register your models here.
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(AnswerLike)
admin.site.register(QuestionLike)
admin.site.register(Tag)
admin.site.register(Profile)
