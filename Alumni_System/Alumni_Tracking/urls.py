from django.urls import path
from django.conf.urls import url, include
from Alumni_Tracking import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register, name='user_register'),
    path('login', views.user_login, name='user_login'),
    path('logout', views.user_logout, name='user_logout'),
    url('^dashboard/$', views.user_logged_in, name='user_logged_in'),
    path('recovery', views.forget_password, name='user_recover_password'),
    url(r'^(?P<slug>[\w-]+)/$', views.view_post, name='article'),
    path('create', views.post_create, name='new_post'),
    path('mypost', views.all_post, name='user_posts'),
    url(r'^edit/(?P<post_id>[\d]+)/$', views.update_article, name='user_post_update'),
    path('change-password', views.change_password, name='user_change_password'),
    url(r'^profile/(?P<username>[\w]+)$', views.profile_view, name='user_profile'),
    path('alumni', views.alumni_list, name='alumni_list'),
    url('^oauth/', include('social_django.urls', namespace='social')),
    path('projects', views.list_projects, name='user_projects'),
    path('internships', views.list_internships, name='user_internships'),
    path('events', views.event, name='user_events'),
    url(r'^download/(?P<file_id>[\d]+)/$', views.call_download, name='user_download'),
    url(r'^delete/(?P<file_id>[\d]+)/$', views.call_delete, name='user_delete'),
    path('academic-forms', views.academic_token, name='academic_token'),
    path('chat', views.chats, name='chat_box'),
]
