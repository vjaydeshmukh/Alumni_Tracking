from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


class college(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    user.is_staff = True
    user.is_superuser = False
    college_name = models.CharField(max_length=100, blank=False)
    college_email = models.EmailField(blank=False)
    college_website = models.URLField(blank=False)
    college_address = models.CharField(max_length=300, blank=False)
    college_description = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.college_name


def user_instance_pic(instance, filename):
    return '{0}/{1}/{2}'.format('dp/alumni', instance.user.username, filename)


class alumni(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    profile_pic = models.ImageField(upload_to=user_instance_pic, default='dp/default.png', blank=True)
    company = models.CharField(max_length=50, default='Unknown', blank=False, null=True)
    college = models.ForeignKey(college, on_delete=models.CASCADE, null=True, blank=False)
    graduate = models.CharField(max_length=4, blank=False, null=True)
    about_me = models.CharField(max_length=200, blank=False, null=True)
    verified = models.BooleanField(default=False, null=True)
    is_alumni = models.BooleanField(default=True, null=True, editable=False)

    def __str__(self):
        return self.user.username


class student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    reg_id = models.CharField(max_length=20, null=True, blank=False)
    college = models.ForeignKey(college, on_delete=models.CASCADE, null=True, blank=False)
    is_alumni = models.BooleanField(default=False, null=True, editable=False)
    verified = models.BooleanField(default=True, null=True, editable=False)

    def __str__(self):
        return self.user.username


def user_instance_blog_pic(instance, filename):
    return '{0}/{1}/{2}'.format('blog/images', instance.author.user.username, filename)


class blog(models.Model):
    author = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, null=True, blank=False)
    slug = models.SlugField(max_length=100, null=True, blank=False)
    images = models.ImageField(upload_to=user_instance_blog_pic, default='dp/default.png', null=True)
    publish_date = models.DateTimeField(auto_now_add=True, blank=False, null=True)
    updated = models.DateTimeField(auto_now=True, blank=False, null=True)
    post = models.TextField(blank=True, null=True)
    status = models.CharField(choices=(('draft', 'Draft'), ('publish', 'Publish')), max_length=10, default='draft',
                              null=True)
    views = models.IntegerField(default=0, null=True, blank=False)
    like = models.IntegerField(default=0, null=True, blank=False)

    def __str__(self):
        return self.title


@receiver(pre_save, sender=blog)
def pre_save_slug(sender, **kwargs):
    slug = slugify(kwargs['instance'].title)
    kwargs['instance'].slug = slug


class comments(models.Model):
    post = models.ForeignKey(blog, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    reply = models.ForeignKey('self', related_name='replies', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return '{}-{}'.format(self.post.title, self.user.username)


def user_instance(instance, filename):
    return '{0}/{1}/{2}/{3}'.format('resume', instance.internship.author.user.username, instance.students.reg_id, filename)


class internships(models.Model):
    author = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True)
    working_type = models.CharField(null=True, blank=False, max_length=30)
    skills = models.CharField(null=True, blank=False, max_length=50)
    about = models.CharField(null=True, blank=False, max_length=150)
    stipend = models.CharField(null=True, blank=False, max_length=20)
    organisation = models.CharField(null=True, blank=False, max_length=50)
    title = models.CharField(null=True, blank=False, max_length=50)
    working_in = models.CharField(null=True, blank=False, max_length=30)
    added = models.DateTimeField(auto_now_add=True, null=True, blank=False)

    def __str__(self):
        return self.title


class apply_internship(models.Model):
    students = models.ForeignKey(student, on_delete=models.CASCADE, null=True)
    internship = models.ForeignKey(internships, on_delete=models.CASCADE, null=True)
    resume_upload = models.FileField(upload_to=user_instance, null=True, blank=False, default=None)

    class Meta:
        unique_together = ['students', 'internship']

    def __str__(self):
        return self.internship.author.user.username


class projects(models.Model):
    title = models.CharField(max_length=50, blank=False)
    about = models.CharField(max_length=300, blank=False)
    students = models.CharField(max_length=100, blank=False)
    domain = models.CharField(max_length=50, blank=False)
    money = models.CharField(max_length=20, blank=False)
    college = models.ForeignKey(college, on_delete=models.CASCADE, null=True, blank=False)
    added = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return self.title


class fund_projects(models.Model):
    ex = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True, blank=False)
    project = models.ForeignKey(projects, on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        unique_together = ('ex', 'project')


class Event(models.Model):
    title = models.CharField(max_length=50, blank=False)
    about = models.CharField(max_length=300, blank=False)
    college = models.ForeignKey(college, on_delete=models.CASCADE, null=True, blank=False)
    author = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True, blank=False)
    event_on = models.DateField(null=True, blank=False)
    address = models.CharField(null=True, blank=False, max_length=150)
    mobile = models.CharField(null=True, blank=False, max_length=10)
    email = models.EmailField(null=True, blank=False)

    def __str__(self):
        return self.title


class attend_event(models.Model):
    attendee = models.ForeignKey(student, on_delete=models.CASCADE, null=True, blank=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=False)

    class Meta:
        unique_together = ['attendee', 'event']

    def __str__(self):
        return self.attendee.user.username


def user_instance_file(instance, filename):
    return '{0}/{1}/{2}/{3}'.format('resume', instance.profile.user.username, 'carrier', filename)


class file_handler(models.Model):
    profile = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True)
    file = models.FileField(null=True, upload_to=user_instance_file, default=None, blank=True)

    def __str__(self):
        return self.profile.user.username


class public_notice(models.Model):
    title = models.CharField(max_length=100, rel='title')
    strap = models.DateTimeField(auto_now_add=True)
    notice = models.CharField(max_length=300)


class add_friend(models.Model):
    profile = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True, related_name='sender')
    friends = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True)
    confirm = models.BooleanField(default=False, null=True)

    class Meta:
        unique_together = ['profile', 'friends']

    def __str__(self):
        return self.profile.user.username


class message_model(models.Model):
    sender = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True, related_name='sender_m')
    receive = models.ForeignKey(alumni, on_delete=models.CASCADE, null=True, related_name='receiver_m')
    content = models.CharField(max_length=1000, blank=False, null=True)
    strap = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.user.username
