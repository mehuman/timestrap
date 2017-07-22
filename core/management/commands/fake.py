from random import randint, choice
from datetime import timedelta, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from faker import Factory
import pytz

from core.models import Client, Entry, Project, Task, Invoice


class Command(BaseCommand):
    help = 'Generates a bunch of fake clients, projects, and entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            dest='iterations',
            default=5,
            help='The amount of data we add do the database'
        )

    def handle(self, *args, **kwargs):
        fake = Factory.create()
        verbosity = kwargs['verbosity']
        iterations = kwargs['iterations']
        if not iterations:
            iterations = 5

        for i in range(randint(iterations, iterations*2)):
            task_name = (fake
                         .sentence(nb_words=3, variable_nb_words=True)
                         .replace('.', '')
                         .capitalize())
            Task.objects.create(
                name=task_name,
                hourly_rate=Decimal(
                    '%d.%d' % (randint(0, 200), randint(0, 99)))
            )

        for i in range(iterations):
            Client.objects.create(name=fake.company())

        for client in Client.objects.iterator():
            project_iterations = randint(iterations, iterations*2)
            for i in range(project_iterations):
                estimated = choice([True, False])
                estimate = None
                if estimated:
                    estimate = timedelta(hours=randint(5, 150))
                project_name = (fake
                                .sentence(nb_words=3, variable_nb_words=True)
                                .replace('.', '')
                                .capitalize())
                Project.objects.create(
                    client=client,
                    estimate=estimate,
                    name=project_name
                )

        for i in range(iterations):
            fake_user = fake.simple_profile(sex=None)
            username = fake_user['username']
            email = fake_user['mail']
            password = fake.password(
                length=10,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
            )
            User.objects.create_user(username, email, password)

        users = User.objects.all()
        projects = Project.objects.all()
        tasks = Task.objects.all()

        for project in projects:
            entry_iterations = randint(iterations*2, iterations*4)
            for i in range(entry_iterations):
                date = fake.date_time_between(
                    start_date='-30d',
                    end_date='now',
                    tzinfo=None
                )
                duration = timedelta(
                    hours=randint(0, 3),
                    minutes=randint(1, 60)
                )
                Entry.objects.create(
                    project=project,
                    user=choice(users),
                    task=choice(tasks),
                    date=date,
                    duration=duration,
                    note=fake.sentence(nb_words=6, variable_nb_words=True)
                )

        one_week_ago = datetime.now() - timedelta(days=7)
        one_week_ago = one_week_ago.date()
        for project in Project.objects.all():
            has_paid = choice([True, False])
            if has_paid:
                paid = datetime.now(pytz.timezone('US/Eastern'))
            else:
                paid = None
            invoice = Invoice.objects.create(client=project.client, paid=paid)
            for entry in project.entries.iterator():
                if entry.date < one_week_ago:
                    invoice.entries.add(entry)

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS('Successfully added fake data.')
            )
