import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from ...models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


class Command(BaseCommand):
    help = "Fills the database with test data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Ratio for filling the database")

    def create_username(self, i):
        return f"username{i}"

    def create_email(self, i):
        return f"user{i}@example.com"

    def create_question_title(self, i):
        return f"Question title {i}"

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
            user = User(username=username, email=email, password="password")
            users.append(user)
        User.objects.bulk_create(users, ignore_conflicts=True)
        return User.objects.all()

    def create_profiles(self, users):
        profiles = []
        for user in users:
            profile = Profile(user=user)
            profiles.append(profile)
        Profile.objects.bulk_create(profiles)

    def create_tags(self):
        tag_names = {f"tag{i}" for i in range(1, self.ratio + 1)}
        tags = [Tag(title=name) for name in tag_names]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        return Tag.objects.all()

    def create_questions(self, users):
        return [
            Question(
                title=self.create_question_title(i),
                content=self.create_question_content(i),
                author=random.choice(users),
            )
            for i in range(1, self.ratio * 10 + 1)
        ]

    def create_answers(self, questions, users):
        return [
            Answer(
                content=self.create_answer_content(i),
                author=random.choice(users),
                question=random.choice(questions),
            )
            for i in range(1, self.ratio * 100 + 1)
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
        self.ratio = options["ratio"]
        self.stdout.write("Starting to fill the database...")

        with transaction.atomic():
            users = self.create_users()
            print("users created")
            self.create_profiles(users)
            print("profiles created")

            tags = list(self.create_tags())
            print("tags created")

            questions = self.create_questions(users)

            Question.objects.bulk_create(questions)
            print("questions created")
            for question in Question.objects.all():
                selected_tags = random.sample(tags, k=random.randint(1, 5))
                question.tags.add(*selected_tags)

            answers = self.create_answers(questions, users)
            Answer.objects.bulk_create(answers)
            print("answers created")

            self.create_question_likes(questions, users)
            print("question_likes created")
            self.create_answer_likes(answers, users)
            print("answer_likes created")

        self.stdout.write(self.style.SUCCESS("Successfully filled the database!"))
