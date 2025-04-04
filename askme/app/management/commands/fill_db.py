import os
import random
import time
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from ...models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = 'Fills the database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio for filling the database')

    def create_username(self, i):
        return f'username{i}'

    def create_email(self, i):
        return f'user{i}@example.com'

    def create_question_title(self, i):
        return f'Question title {i}'

    def create_question_content(self, i):
        return (
            f"This is a sample question content number {i}. "
            f"It covers various aspects of the topic. "
            f"Here are some more details and explanations regarding the question."
        )

    def create_answer_content(self, i):
        return (
            f"This is an answer to the question number {i}. "
            f"The answer elaborates on the topic and provides useful insights. "
            f"Additionally, it suggests practical approaches to tackle similar issues."
        )

    def create_users(self):
        users = []
        for i in range(1, self.ratio + 1):
            username = self.create_username(i)
            email = self.create_email(i)
            user = User(username=username, email=email, password='password')
            users.append(user)
        User.objects.bulk_create(users, ignore_conflicts=True)
        return User.objects.all()

    def create_profiles(self, users):
        img_files = [f'{i}.jpg' for i in range(1, 7)]
        profiles = []

        for user in users:
            avatar_name = random.choice(img_files)
            profile = Profile(user=user, avatar=avatar_name)
            profiles.append(profile)

        Profile.objects.bulk_create(profiles)

    def create_tags(self):
        tag_names = {f'tag{i}' for i in range(1, self.ratio + 1)}
        tags = [Tag(title=name) for name in tag_names]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        return Tag.objects.all()

    def create_questions(self, users):
        return [
            Question(
                title=self.create_question_title(i),
                content=self.create_question_content(i),
                author=random.choice(users)
            ) for i in range(1, self.ratio * 10 + 1)
        ]

    def create_answers(self, questions, users):
        return [
            Answer(
                content=self.create_answer_content(i),
                author=random.choice(users),
                question=random.choice(questions)
            ) for i in range(1, self.ratio * 100 + 1)
        ]

    def create_question_likes(self, questions, users):
        likes = [
            QuestionLike(user=random.choice(users), question=random.choice(questions))
            for _ in range(self.ratio * 100)
        ]
        QuestionLike.objects.bulk_create(likes, ignore_conflicts=True)

    def create_answer_likes(self, answers, users):
        likes = [
            AnswerLike(user=random.choice(users), answer=random.choice(answers))
            for _ in range(self.ratio * 100)
        ]
        AnswerLike.objects.bulk_create(likes, ignore_conflicts=True)

    def handle(self, *args, **options):
        self.ratio = options['ratio']
        self.stdout.write('Starting to fill the database...')
        start_time = time.perf_counter()

        with transaction.atomic():
            users = self.create_users()
            self.stdout.write('created users')
            self.create_profiles(users)
            self.stdout.write('created profiles')

            tags = list(self.create_tags())
            self.stdout.write('created tags')

            questions = self.create_questions(users)
            self.stdout.write('created questions')
            Question.objects.bulk_create(questions)

            for question in Question.objects.all():
                selected_tags = random.sample(tags, k=random.randint(1, 5))
                question.tags.add(*selected_tags)
            self.stdout.write('added tags')

            answers = self.create_answers(questions, users)
            self.stdout.write('created answers')
            Answer.objects.bulk_create(answers)

            self.create_question_likes(questions, users)
            self.stdout.write('created likes for questions')
            self.create_answer_likes(answers, users)

        self.stdout.write(self.style.SUCCESS(f'Successfully filled the database! It took {(time.perf_counter() - start_time)::.4f} seconds'))