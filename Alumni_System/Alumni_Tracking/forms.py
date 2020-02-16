from django import forms
from .models import *
from .collection import list_college
import re


class alumni_details_basic(forms.Form, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), min_length=6,
                               label='Password', required=True)
    v_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), min_length=6,
                                 label='Verify Password', required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='First Name',
                                 required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Last Name',
                                required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Username',
                               max_length=150, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Enter your email id:',
                             required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class alumni_details_more(forms.ModelForm):
    graduate = forms.CharField(max_length=4,
                               widget=forms.NumberInput(attrs={'maxlength': '4', 'class': 'form-control'}),
                               label='Graduation Year',
                               help_text='Like 2022', required=True)
    profile_pic = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), label='Display Picture',
                                   required=False)
    about_me = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='About me', required=True,
                               help_text='Write something about you', strip=True, max_length=200)

    class Meta:
        model = alumni
        fields = ('profile_pic', 'graduate', 'college', 'about_me')


class login_form(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=True, label='Email')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True,
                               label='Password')
    remember_me = forms.BooleanField(required=False, label='Remember me', widget=forms.CheckboxInput())
    login_as = forms.ChoiceField(required=True, choices=(('1', 'Alumni'), ('2', 'Student')), label='Login as')


class otp_verify(forms.Form):
    key = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True, label='Enter OTP')


class recover_password(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=150,
                               label='Enter your username:', required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Enter your email id:',
                             required=True)
    login_as = forms.ChoiceField(required=True, choices=(('1', 'Alumni'), ('2', 'Student')), label='Choose your role')


class post_create_form(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title', required=True,
                            strip=True, max_length=100)
    post = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='Content', required=True,
                           max_length=50000)

    class Meta:
        model = blog
        fields = ('title', 'post', 'images', 'status')


class change_password_form(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), min_length=6,
                               label='Current Password')
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), min_length=6,
                                   label='New Password')
    new_verify_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), min_length=6,
                                          label='Verify Password')

    def clean(self):
        all_clean = super().clean()
        pass_2 = all_clean['new_password']
        pass_3 = all_clean['new_verify_password']

        if pass_2 != pass_3:
            raise forms.ValidationError('New password doesn\'t matched')


class comment_form(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '8', 'cols': '80',
                                                           'placeholder': 'Enter your comment or reply'}),
                              label='Comment', max_length=200,
                              required=True)

    class Meta:
        model = comments
        fields = ('comment',)


class internship_form(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title',
                            max_length=50, required=True)
    working_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Working Type',
                                   max_length=30, required=True, help_text='Example: Work from home')
    working_in = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Duration',
                                 max_length=30, required=True, help_text='Example: 3 months')
    organisation = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Organisation',
                                   max_length=50, required=True)
    skills = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Required Skills',
                             max_length=50, required=True)
    about = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='About Internship',
                            required=True,
                            help_text='Write something about internship', strip=True, max_length=150)
    stipend = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Stipend',
                              max_length=20, required=True)

    class Meta:
        model = internships
        fields = ('title', 'working_type', 'working_in', 'organisation', 'skills', 'about', 'stipend')


class apply_internship_form(forms.ModelForm):
    resume_upload = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}), label='Upload',
                                    help_text='Upload your resume')

    class Meta:
        model = apply_internship
        fields = ('resume_upload',)


class event_form(forms.ModelForm):
    event_on = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control'}), input_formats=['%d-%m-%Y'], help_text='22-01-2020')
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title',
                            max_length=50, required=True)
    about = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='About', required=True,
                            help_text='Write about event', strip=True, max_length=300)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Address', required=True,
                              strip=True, max_length=150)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Enter your email id:',
                             required=True)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=10)

    class Meta:
        model = Event
        fields = '__all__'
        exclude = ('college', 'author',)

    def clean(self):
        all_clean = super().clean()
        if not bool(re.search('^[\d]{10}$', all_clean['mobile'])):
            raise forms.ValidationError('Mobile number is not valid')
