from django.contrib import admin
from Alumni_Tracking.models import *
from django.contrib.auth.models import User, Group


class blogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'views', 'like', 'status')
    list_filter = ('publish_date', 'author__user__username')
    search_fields = ('title',)
    list_editable = ('status',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return blog.objects.all().order_by('-publish_date')
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return blog.objects.filter(author__college__user_id=col_id)


class alumniAdmin(admin.ModelAdmin):
    list_filter = ('college', 'graduate', 'company')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return alumni.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return alumni.objects.filter(college__user_id=col_id)


class internshipsAdmin(admin.ModelAdmin):
    list_display = ('title', 'organisation', 'working_type')
    list_filter = ('organisation', 'author__college__college_name', 'author__user__username', 'working_type')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return internships.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return internships.objects.filter(author__college__user_id=col_id)


class apply_internAdmin(admin.ModelAdmin):
    list_filter = ('students__user__username', 'students__college__college_name', 'internship__title',
                   'internship__organisation', 'internship__author__user__username')
    search_fields = ('students__reg_id',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return apply_internship.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return apply_internship.objects.filter(internship__author__college__user_id=col_id)


class commentsAdmin(admin.ModelAdmin):
    list_filter = ('post__author__user__username', 'post__publish_date', 'post__status', 'user__username')
    search_fields = ('post__title',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return comments.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return comments.objects.filter(post__author__college__user_id=col_id)


class studentAdmin(admin.ModelAdmin):
    list_filter = ('college__college_name',)
    search_fields = ('user__username', 'reg_id')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return student.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return student.objects.filter(college__user_id=col_id)


class noticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'notice', 'strap')
    list_filter = ('strap',)
    search_fields = ('title', 'notice')


class projectAdmin(admin.ModelAdmin):
    list_display = ('title', 'about', 'money')
    list_filter = ('domain',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return projects.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return projects.objects.filter(college__user_id=col_id)


class fund_projectAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        if request.user.is_superuser:
            return fund_projects.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return fund_projects.objects.filter(ex__college__user_id=col_id)


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'about', 'event_on')
    list_filter = ('email',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return Event.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return Event.objects.filter(author__college__user_id=col_id)


class Att_EventAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        if request.user.is_superuser:
            return attend_event.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return attend_event.objects.filter(event__author__college__user_id=col_id)


class file_admin(admin.ModelAdmin):

    def get_queryset(self, request):
        if request.user.is_superuser:
            return file_handler.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return file_handler.objects.filter(profile__college__user_id=col_id)


class friendAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        if request.user.is_superuser:
            return add_friend.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return add_friend.objects.filter(profile__college__user_id=col_id)


class messageAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        if request.user.is_superuser:
            return message_model.objects.all()
        else:
            try:
                col_id = college.objects.get(user=request.user).user_id
            except college.DoesNotExist:
                return college.objects.none()
            return message_model.objects.filter(sender__college__user_id=col_id)


admin.site.site_header = "Alumni's Call Admin"
admin.site.site_title = "Alumni's Call Admin Portal"
admin.site.index_title = "Welcome to Alumni's Call"
admin.site.register(college)
admin.site.register(alumni, alumniAdmin)
admin.site.register(blog, blogAdmin)
admin.site.register(internships, internshipsAdmin)
admin.site.register(apply_internship, apply_internAdmin)
admin.site.register(student, studentAdmin)
admin.site.register(comments, commentsAdmin)
admin.site.register(projects, projectAdmin)
admin.site.register(fund_projects, fund_projectAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(attend_event, Att_EventAdmin)
admin.site.register(file_handler, file_admin)
admin.site.register(public_notice, noticeAdmin)
admin.site.register(add_friend, friendAdmin)
admin.site.register(message_model)
admin.site.unregister(User)
admin.site.unregister(Group)
