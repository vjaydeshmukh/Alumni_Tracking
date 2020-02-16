from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.encoding import smart_str
from .collection import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from datetime import date

otp = None


def home(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    events = Event.objects.all().order_by('-event_on')[:5]
    if request.user.is_authenticated:
        profile = object_collector(request)
        context = {
            'profile': profile,
            'notices': public_notice.objects.all().order_by('-strap')[:5],
            'notify': collect_notifications(request)
        }
    else:
        context = {}
    context['event_side'] = events
    return render(request, 'home.html', context)


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_logged_in'))

    if mobile_check(request):
        return render(request, 'stop.html')

    f1 = alumni_details_basic()
    f2 = alumni_details_more()

    if request.method == 'POST':
        f1 = alumni_details_basic(data=request.POST)
        f2 = alumni_details_more(data=request.POST, files=request.FILES)

        if f1.is_valid() and f2.is_valid():
            email = f1.cleaned_data['email']
            if bool(re.search('mitaoe.ac.in$', str(email))):
                return render(request, 'register.html', context={'form_basic': f1, 'form_more': f2,
                                                                 'error': 'Use your primary email'})
            if alumni.objects.filter(user__email=email).exists():
                return render(request, 'register.html', context={'form_basic': f1, 'form_more': f2,
                                                                 'error': 'Email is already registered.'})
            elif f1.cleaned_data['password'] != f1.cleaned_data['v_password']:
                return render(request, 'home.html', context={'form_basic': f1, 'form_more': f2,
                                                             'error': 'Password does not matched'})

            basic_details = f1.save()
            basic_details.email = email
            basic_details.set_password(basic_details.password)
            basic_details.save()
            more_detail = f2.save(commit=False)
            more_detail.user = basic_details

            if 'profile_pic' in request.FILES:
                more_detail.profile_pic = request.FILES.get('profile_pic')

            more_detail.save()

            return render(request, 'home.html', context={'registered': True})

    return render(request, 'register.html', context={'form_basic': f1, 'form_more': f2})


def user_login(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_logged_in'))
    f1 = login_form()

    if request.method == 'POST':
        f1 = login_form(data=request.POST)

        if f1.is_valid():
            email = f1.cleaned_data['email']
            password = f1.cleaned_data['password']
            login_as = f1.cleaned_data['login_as']
            if not bool(f1.cleaned_data['remember_me']):
                request.session.set_expiry(0)
                request.session.save()

            if login_as == '1':
                try:
                    profile = alumni.objects.get(user__email=email)
                except alumni.DoesNotExist:
                    return render(request, 'login.html', context={'login_form': f1,
                                                                  'message': 'Email id is not registered'})

                user = authenticate(request, username=profile.user.username, password=password)

                if user is None:
                    return render(request, 'login.html',
                                  context={'login_form': f1, 'message': 'Wrong Password Dikara!!!'})
                else:
                    login(request, user)
                    return HttpResponseRedirect(reverse('user_logged_in'))

            elif login_as == '2':
                try:
                    normal_profile = student.objects.get(user__email=email)
                except student.DoesNotExist:
                    return render(request, 'login.html',
                                  context={'login_form': f1, 'message': 'Email id is not registered'})

                user = authenticate(request, username=normal_profile.user.username, password=password)

            if user is None:
                return render(request, 'login.html',
                              context={'login_form': f1, 'message': 'Wrong Password Dikara!!!'})
            elif user:
                login(request, user)
                return HttpResponseRedirect(reverse('user_logged_in'))
    return render(request, 'login.html', context={'login_form': f1})


@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    request.session.flush()
    return render(request, 'home.html', context={'message': 'You logged out successfully.'})


def forget_password(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_logged_in'))

    f1 = recover_password()

    if request.method == 'POST':
        f1 = recover_password(data=request.POST)

        if f1.is_valid():
            username = f1.cleaned_data['username']
            email = f1.cleaned_data['email']
            role = f1.cleaned_data['login_as']
            if role == '1':
                try:
                    profile = alumni.objects.get(user__username=username, user__email=email)
                except alumni.DoesNotExist:
                    return render(request, 'forget_password.html', context={'recovery': f1,
                                                                            'message': 'Provided details are wrong'})
            elif role == '2':
                try:
                    profile = student.objects.get(user__username=username, user__email=email)
                except student.DoesNotExist:
                    return render(request, 'forget_password.html', context={'recovery': f1,
                                                                            'message': 'Provided details are wrong'})
            temp_password = generate_password()
            profile.user.set_password(temp_password)
            profile.user.save(force_update=True, update_fields=['password', ])
            recover_mail(email, temp_password)
            return HttpResponseRedirect(reverse('user_login'))

    return render(request, 'forget_password.html', context={'recovery': f1})


@login_required(login_url='user_login')
def user_logged_in(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    global otp
    profile = object_collector(request)

    if not profile.verified and len(str(otp)) != 6:
        otp = generate_otp(email=str(profile.user.email))

    popular_post = post_collector(request)
    new_internship = internships_collector(request)

    f1 = otp_verify()

    if request.method == 'POST':
        f1 = otp_verify(data=request.POST)

        # --------------------------------------------------------------------------------------------------------------

        if f1.is_valid() and not profile.verified:
            key = f1.cleaned_data['key']
            if len(str(key)) == 6 and str(otp) == str(key):
                profile.verified = True
                profile.save(update_fields=['verified'])
                otp = None
                return HttpResponseRedirect(reverse('user_logged_in'))
            else:
                return render(request, 'dashboard.html',
                              context={'profile': profile, 'otp_verify': f1,
                                       'message': 'OTP is not valid...please verify your otp'})

    # -------------------------------------------------------------------------------------------------------------------

    search = request.GET.get('search')
    flag = False

    try:
        college_id = alumni.objects.get(user=request.user).college_id
    except alumni.DoesNotExist:
        college_id = student.objects.get(user=request.user).college_id

    if search:
        post = blog.objects.filter(Q(title__icontains=search, author__college_id=college_id) |
                                   Q(author__user__first_name__iexact=search, author__college_id=college_id) |
                                   Q(author__user__last_name__iexact=search, author__college_id=college_id)) \
            .exclude(status='draft').order_by('-publish_date')

        if not post.exists():
            flag = True

    else:
        post = blog.objects.filter(author__college_id=college_id).exclude(status='draft').order_by('-publish_date')

    paginator = Paginator(post, 5)
    page_num = request.GET.get('page')

    try:
        post = paginator.page(page_num)
    except PageNotAnInteger:
        post = paginator.page(1)
        page_num = 1
    except EmptyPage:
        post = paginator.num_pages

    if page_num is None:
        page_num = 1

    event_side = event_collector(request)

    if profile:
        context = {'alumni': profile, 'otp_verify': f1, 'posts': post, 'page_upper': int(page_num) + 5,
                   'page_lower': int(page_num), 'profile': profile, 'popular_post': popular_post,
                   'new_intern': new_internship, 'event_side': event_side, 'notify': collect_notifications(request)}

    if flag:
        context = {'alumni': profile, 'otp_verify': f1, 'message': str(str(search) + ' not found!!!'), 'page_upper': 0,
                   'page_lower': 0, 'profile': profile, 'popular_post': popular_post, 'new_intern': new_internship,
                   'event_side': event_side, 'notify': collect_notifications(request)}

    if profile.verified:
        context.pop('otp_verify')
    return render(request, 'dashboard.html', context=context)


@login_required(login_url='user_login')
def view_post(request, slug):
    if mobile_check(request):
        return render(request, 'stop.html')

    f1 = comment_form()
    profile = object_collector(request)
    popular_post = post_collector(request)
    new_internship = internships_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    try:
        post = blog.objects.get(slug=slug)
    except blog.DoesNotExist:
        return HttpResponseRedirect(reverse('user_logged_in'))

    try:
        all_comment = comments.objects.filter(post=post, reply=None).order_by('-datetime')
    except comments.DoesNotExist:
        pass

    if request.user != post.author.user:
        post.views += 1
        post.save(update_fields=['views'])

    if request.method == 'POST':

        f1 = comment_form(request.POST or None)

        if f1.is_valid():

            reply_id = request.POST.get('reply_id')
            comment_new = None
            if reply_id:
                comment_new = comments.objects.get(id=reply_id)
            comment = comments.objects.create(post=post, user=request.user, comment=f1.cleaned_data['comment'],
                                              reply=comment_new)
            comment.save()
        if 'liked_it' in request.POST:
            if str(post.id) == str(request.POST.get('liked_it')) and request.user != post.author.user:
                post.like += 1
                post.save(update_fields=['like'])

    event_side = event_collector(request)

    context = {
        'post': post,
        'comments': all_comment,
        'form': f1,
        'profile': profile,
        'popular_post': popular_post,
        'new_intern': new_internship,
        'event_side': event_side,
        'notify': collect_notifications(request)
    }

    return render(request, 'article.html', context=context)


@login_required(login_url='user_login')
def post_create(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    profile = object_collector(request)
    if not profile.verified or not profile.is_alumni:
        return HttpResponseRedirect(reverse('user_logged_in'))

    f1 = post_create_form()

    search = request.GET.get('search')

    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    if request.method == 'POST':
        f1 = post_create_form(data=request.POST, files=request.FILES or None)

        if f1.is_valid():

            try:
                profile = alumni.objects.get(user=request.user)
            except alumni.DoesNotExist:
                return render(request, 'article.html',
                              context={'form': f1, 'message': 'Not have sufficient permission'})

            blog_post = f1.save(commit=False)
            blog_post.author = profile
            blog_post.save()

            return HttpResponseRedirect(reverse('user_logged_in'))

    context = {
        'form': f1,
        'profile': profile,
        'notify': collect_notifications(request),
    }
    return render(request, 'new_article.html', context)


@login_required(login_url='user_login')
def all_post(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    profile = object_collector(request)
    if not profile.verified or not profile.is_alumni:
        return HttpResponseRedirect(reverse('user_logged_in'))

    list_all_post = blog.objects.filter(author__user=request.user).order_by('-publish_date')
    paginator = Paginator(list_all_post, 6)
    page_num = request.GET.get('page')

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    try:
        list_all_post = paginator.get_page(page_num)
    except PageNotAnInteger:
        list_all_post = paginator.get_page(1)
        page_num = 1
    except EmptyPage:
        list_all_post = paginator.num_pages

    if page_num is None:
        page_num = 1

    context = {
        'list_posts': list_all_post,
        'message': 'Write something nigga to see your contribution!!!',
        'page_upper': int(page_num) + 5,
        'page_lower': int(page_num),
        'profile': profile,
        'notify': collect_notifications(request),
    }

    if request.method == 'POST':

        if 'delete_post' in request.POST:
            try:
                del_post = blog.objects.get(id=request.POST.get('delete_post'))
                del_post.delete()
            except blog.DoesNotExist:
                pass

    return render(request, 'my_post.html', context)


@login_required(login_url='user_login')
def update_article(request, post_id):
    if mobile_check(request):
        return render(request, 'stop.html')

    profile = object_collector(request)
    if not profile.verified or not profile.is_alumni:
        return HttpResponseRedirect(reverse('user_logged_in'))

    try:
        post = blog.objects.get(id=post_id)
    except blog.DoesNotExist:
        return HttpResponseRedirect(reverse('user_posts'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    update_form = post_create_form(instance=post)

    if request.method == 'POST':
        update_form = post_create_form(instance=post, data=request.POST, files=request.FILES or None)

        if update_form.is_valid():
            update_form.save()
            return render(request, 'update_article.html', context={'update_post': update_form,
                                                                   'message': 'Post Update Successfully!!!',
                                                                   'profile': profile,
                                                                   'notify': collect_notifications(request)})
        elif not update_form.is_valid():
            return render(request, 'update_article.html', context={'update_post': update_form,
                                                                   'message_error': 'Something went Wrong!!!',
                                                                   'profile': profile,
                                                                   'notify': collect_notifications(request)})

    return render(request, 'update_article.html',
                  context={'update_post': update_form, 'profile': profile, 'notify': collect_notifications(request)})


@login_required(login_url='user_login')
def change_password(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    f1 = change_password_form()

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    if request.method == 'POST':
        f1 = change_password_form(data=request.POST)

        if f1.is_valid():
            pass_1 = f1.cleaned_data['password']
            pass_2 = f1.cleaned_data['new_password']

            if request.user.check_password(pass_1):
                request.user.set_password(pass_2)
                request.user.save(update_fields=['password'])

                return render(request, 'changepassword.html',
                              context={'form': f1, 'message': 'Password updated successfully', 'profile': profile,
                                       'notify': collect_notifications(request)})

            else:
                return render(request, 'changepassword.html',
                              context={'form': f1, 'message_error': 'Password is incorrect', 'profile': profile,
                                       'notify': collect_notifications(request)})

    return render(request, 'changepassword.html',
                  context={'form': f1, 'profile': profile, 'notify': collect_notifications(request)})


@login_required(login_url='user_login')
def profile_view(request, username):
    if mobile_check(request):
        return render(request, 'stop.html')

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    try:
        college_id = alumni.objects.get(user=request.user).college_id
    except alumni.DoesNotExist:
        college_id = student.objects.get(user=request.user).college_id

    try:
        profiles = alumni.objects.get(user__username=username, college_id=college_id)
    except alumni.DoesNotExist:
        logout(request)

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    f1 = alumni_details_basic(instance=profiles.user)
    f2 = alumni_details_more(instance=profiles)
    c_college = profile.college
    if request.method == 'POST':

        if 'upload_file' in request.FILES:
            for file in request.FILES.getlist('upload_file'):
                file_save = file_handler.objects.create(profile=profile, file=file)
                file_save.save()

        if 'update_profile' in request.POST:
            if request.user.username == username:
                return render(request, 'profile.html', context={'form_1': f1, 'form_2': f2, 'edit_show': True,
                                                                'profiles': profiles, 'profile': profile,
                                                                'notify': collect_notifications(request)})

        f2 = alumni_details_more(instance=profiles, data=request.POST, files=request.FILES or None)
        if f2.is_valid():
            f2.save()
            profile.college = c_college
            profile.save(update_fields=['college'])
            return render(request, 'profile.html', context={'edit': True, 'profile': profile,
                                                            'message': 'Profile updated successfully!!!',
                                                            'profiles': profiles,
                                                            'notify': collect_notifications(request)})
        elif not f2.is_valid():
            return render(request, 'profile.html',
                          context={'form_1': f1, 'form_2': f2, 'edit': True, 'edit_show': True, 'profile': profile,
                                   'message_error': 'Something went wrong!!!', 'profiles': profiles,
                                   'notify': collect_notifications(request)})

    if request.user.username == username:
        context = {
            'edit': True,
            'profile': profile,
            'profiles': profiles,
            'notify': collect_notifications(request)
        }

    else:
        context = {
            'edit': False,
            'profile': profile,
            'profiles': profiles,
            'notify': collect_notifications(request)
        }

    if profile.is_alumni:
        context['files'] = file_handler.objects.filter(profile=profile)
    return render(request, 'profile.html', context)


@login_required(login_url='user_login')
def alumni_list(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    flag = False

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    friend_id = request.GET.get('friend_id')
    if friend_id:
        friend, created = add_friend.objects.get_or_create(profile=profile,
                                                           friends=alumni.objects.get(user__username=friend_id))
        if not created:
            friend.save()

    cancel_friend_id = request.GET.get('cancel_friend_id')
    if cancel_friend_id:
        friend = add_friend.objects.get(profile=profile,
                                        friends=alumni.objects.get(
                                            user__username=cancel_friend_id)) or add_friend.objects.get(
            profile=alumni.objects.get(user__username=cancel_friend_id),
            friends=profile)
        friend.delete()

    confirm_friend_id = request.GET.get('confirm_friend_id')
    if confirm_friend_id:
        friend = add_friend.objects.get(profile=alumni.objects.get(user__username=confirm_friend_id), friends=profile)
        friend.confirm = True
        friend.save(update_fields=['confirm', ])

    try:
        college_id = alumni.objects.get(user=request.user).college_id
    except alumni.DoesNotExist:
        college_id = student.objects.get(user=request.user).college_id

    search_alumni = request.GET.get('search_alumni')
    if search_alumni:
        all_alumni = alumni.objects.filter((Q(user__first_name__icontains=search_alumni, verified=True,
                                              college_id__exact=college_id) | Q(user__last_name__icontains=search_alumni
                                                                                , verified=True,
                                                                                college_id__exact=college_id) |
                                            Q(company__icontains=search_alumni, verified=True,
                                              college_id__exact=college_id) | Q(graduate__iexact=search_alumni,
                                                                                verified=True,
                                                                                college_id__exact=college_id))).order_by \
            ('-user__first_name')

        if not all_alumni.exists():
            flag = True
    else:
        all_alumni = alumni.objects.filter(college_id__exact=college_id).order_by(
            '-user__first_name')

    paginator = Paginator(all_alumni, 9)
    page_num = request.GET.get('page')

    try:
        all_alumni = paginator.get_page(page_num)
    except PageNotAnInteger:
        all_alumni = paginator.get_page(1)
    except EmptyPage:
        all_alumni = paginator.num_pages

    if page_num is None:
        page_num = 1

    context = {
        'alumnies': all_alumni,
        'page_upper': int(page_num) + 5,
        'page_lower': int(page_num),
        'profile': profile,
        'notify': collect_notifications(request)
    }

    if flag:
        context = {
            'message': str(str(search_alumni) + ' not found!!!'),
            'profile': profile,
        }

    return render(request, 'alumni_list.html', context)


@login_required(login_url='user_login')
def list_projects(request):
    flag = False

    if mobile_check(request):
        return render(request, 'stop.html')

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    try:
        college_id = alumni.objects.get(user=request.user).college_id
    except alumni.DoesNotExist:
        college_id = student.objects.get(user=request.user).college_id

    all_projects = projects.objects.filter(college_id=college_id)

    if request.method == 'POST':
        fund_id = request.POST.get('fund_id')

        if not fund_projects.objects.filter(project_id=fund_id).exists():
            funded_now = fund_projects.objects.create(ex=profile, project_id=fund_id)
            funded_now.save()
            flag = True
        else:
            flag = None

    if flag:
        context = {
            'all_projects': all_projects,
            'notify': collect_notifications(request),
            'profile': profile,
            'pop_up': True,
        }

    else:
        context = {
            'all_projects': all_projects,
            'notify': collect_notifications(request),
            'profile': profile,
        }
    if flag is None:
        context['already_funded'] = True

    return render(request, 'projects.html', context)


@login_required(login_url='user_login')
def list_internships(request):
    flag = False

    if mobile_check(request):
        return render(request, 'stop.html')

    f1 = internship_form()
    f2 = apply_internship_form()

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    try:
        college_id = alumni.objects.get(user=request.user).college_id
    except alumni.DoesNotExist:
        college_id = student.objects.get(user=request.user).college_id

    jobs = internships.objects.filter(author__college_id=college_id).order_by('-title')
    paginator = Paginator(jobs, 7)
    page_num = request.GET.get('page')

    try:
        jobs = paginator.get_page(page_num)
    except PageNotAnInteger:
        jobs = paginator.get_page(1)
        page_num = 1
    except EmptyPage:
        jobs = paginator.num_pages

    if page_num is None:
        page_num = 1

    if request.method == 'POST':
        f1 = internship_form(data=request.POST)
        f2 = apply_internship_form(data=request.POST, files=request.FILES or None)

        if f1.is_valid():
            title = f1.cleaned_data['title']
            if not internships.objects.filter(title=title).exists():
                intern = f1.save(commit=False)
                intern.author = alumni.objects.get(user=request.user)
                intern.save()
                return HttpResponseRedirect(reverse('user_internships'))

        if f2.is_valid():
            intern = f2.save(commit=False)
            i_ide = request.POST.get('internship_id')

            if not apply_internship.objects.filter(id=int(i_ide), students__user=request.user).exists():
                try:
                    intern.internship = internships.objects.get(id=i_ide)
                    intern.students = student.objects.get(user=request.user)
                    intern.save()
                    flag = None
                except internships.DoesNotExist:
                    pass
            else:
                flag = True

    context = {
        'jobs': jobs,
        'page_upper': int(page_num) + 5,
        'page_lower': int(page_num),
        'job_form': f1,
        'apply_form': f2,
        'profile': profile,
        'notify': collect_notifications(request),
    }

    if flag:
        context['already_applied'] = True

    if flag is None:
        context['applied'] = True
    return render(request, 'internships.html', context)


@login_required(login_url='user_login')
def event(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    already_registerd = False
    message = False
    event_confirmed = False
    f1 = event_form()
    event_side = event_collector(request)
    profile = object_collector(request)

    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    try:
        college_id = alumni.objects.get(user=request.user).college_id
    except alumni.DoesNotExist:
        college_id = student.objects.get(user=request.user).college_id

    events = Event.objects.filter(college_id__exact=college_id)

    event_id = request.GET.get('attendee_added')

    if event_id:
        if not attend_event.objects.filter(attendee=profile, event_id=event_id).exists():
            plusone = attend_event.objects.create(attendee=profile, event_id=event_id)
            plusone.save()

    if request.method == 'POST':
        f1 = event_form(data=request.POST)

        if f1.is_valid():

            if Event.objects.filter(title=f1.cleaned_data['title'], college_id__exact=college_id).exists():
                already_registerd = True
            else:
                d1 = f1.cleaned_data['event_on']
                d2 = date.today()
                if d2 < d1:
                    event_details = f1.save(commit=False)
                    event_details.college = college.objects.get(id=college_id)
                    event_details.author = alumni.objects.get(user=request.user)
                    event_details.save()
                    event_confirmed = True
                else:
                    message = 'Invalid date is given'

    popular_post = post_collector(request)
    new_internship = internships_collector(request)
    context = {
        'profile': profile,
        'event_form': f1,
        'event_confirmed': event_confirmed,
        'already_registerd': already_registerd,
        'message': message,
        'events': events,
        'event_side': event_side,
        'popular_post': popular_post,
        'new_intern': new_internship,
        'notify': collect_notifications(request),
    }

    return render(request, 'events.html', context)


@login_required(login_url='user_login')
def call_download(request, file_id):
    file = file_handler.objects.get(id=file_id)
    path = file.file.url
    os.chdir(get_media_path(path))
    f_name = os.path.split(file.file.name)[1]
    with open(os.path.join(os.getcwd(), f_name), 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="%s"' % str(f_name)
        response['X-Sendfile'] = smart_str(path)
        return response


@login_required(login_url='user_login')
def call_delete(request, file_id):
    file = file_handler.objects.get(id=file_id)
    os.remove(file.file.path)
    file.delete()
    return HttpResponse("File Deleted Successfully!!!")


@login_required(login_url='user_login')
def academic_token(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    token_number = None
    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    if request.method == 'POST':
        if 'form_type' in request.POST:
            token_number = generate_token(profile, request.POST.get('form_type'))

    context = {
        'profile': profile,
        'notify': collect_notifications(request),
    }
    if token_number is not None:
        context['token_registered'] = token_number

    return render(request, 'acdemictoken.html', context=context)


@login_required(login_url='user_login')
def chats(request):
    if mobile_check(request):
        return render(request, 'stop.html')

    search = request.GET.get('search')
    if search:
        return HttpResponseRedirect('dashboard/?search=%s' % search)

    profile = object_collector(request)
    if not profile.verified:
        return HttpResponseRedirect(reverse('user_logged_in'))

    friends = add_friend.objects.filter(Q(profile=profile, confirm=True) | Q(friends=profile, confirm=True))

    if request.method == 'POST':
        if 'get_message' in request.POST:
            message = request.POST.get('get_message')
        if 'friend_id' in request.POST:
            friend_id = request.POST.get('friend_id')
            msg = message_model.objects.create(sender=profile, content=message,
                                               receive=alumni.objects.get(user__username=friend_id))
            msg.save()

    context = {
        'profile': profile,
        'notify': collect_notifications(request),
        'friends': friends,
    }

    return render(request, 'chatpage.html', context)
