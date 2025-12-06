from django.contrib import admin

from .models import staff, CustomUser, course, session_year, student,TimeTable, student_notification, subject,staff_notification,staff_leave,staff_feedback,attendance,attendance_report,student_feedback,LeaveType,result



from django.contrib.auth.admin import UserAdmin
# Register your models here.
class UserModel(UserAdmin):
    list_display = ['username','user_type']
admin.site.register(CustomUser,UserModel)
admin.site.register(course)
admin.site.register(session_year)
admin.site.register(student)

admin.site.register(staff)
admin.site.register(subject)
admin.site.register(staff_notification)
admin.site.register(staff_leave)

admin.site.register(student_notification)

admin.site.register(staff_feedback)
admin.site.register(student_feedback)
admin.site.register(attendance)
admin.site.register(attendance_report)
admin.site.register(result)

admin.site.register(LeaveType)
admin.site.register(TimeTable)
