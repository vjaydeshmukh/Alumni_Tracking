from django.contrib import admin
from Alumni_Tracking.models import *


class blogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'views', 'like', 'status')
    list_filter = ('publish_date', 'author__user__username')
    search_fields = ('title',)
    list_editable = ('status',)


class alumniAdmin(admin.ModelAdmin):
    list_filter = ('college', 'graduate', 'company')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')


class internshipsAdmin(admin.ModelAdmin):
    list_display = ('title', 'organisation', 'working_type')
    list_filter = ('organisation', 'author__college__college_name', 'author__user__username', 'working_type')


class apply_internAdmin(admin.ModelAdmin):
    list_filter = ('students__user__username', 'students__college__college_name', 'internship__title',
                   'internship__organisation', 'internship__author__user__username')
    search_fields = ('students__reg_id',)


class commentsAdmin(admin.ModelAdmin):
    list_filter = ('post__author__user__username', 'post__publish_date', 'post__status', 'user__username')
    search_fields = ('post__title',)


class studentAdmin(admin.ModelAdmin):
    list_filter = ('college__college_name',)
    search_fields = ('user__username', 'reg_id')


class noticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'notice', 'strap')
    list_filter = ('strap', )
    search_fields = ('title', 'notice')


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
admin.site.register(projects)
admin.site.register(fund_projects)
admin.site.register(Event)
admin.site.register(attend_event)
admin.site.register(file_handler)
admin.site.register(public_notice, noticeAdmin)
admin.site.register(add_friend)
admin.site.register(message_model)
