import os, django, random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Alumni_System.settings")
django.setup()

from Alumni_Tracking.models import blog, alumni
from django.utils import timezone


def create_post(N):
    fake = Faker()
    for _ in range(N):
        ide = random.randint(1, 2)
        title = fake.name()
        status = 'publish'
        blog.objects.create(author=alumni.objects.get(id=ide), title=title,
                            status=status, publish_date=timezone.now(), updated=timezone.now(), post=fake.text(1000))


create_post(10000)
print('Job done dude!!!')
