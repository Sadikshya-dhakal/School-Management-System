from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
   USER= (
      (1,'hod'),
      (2,'staff'),
      (3,'student'),
    )
   user_type=models.CharField(choices=USER,max_length=50,default=1)
   profile_pic = models.ImageField(upload_to='media/profile_pics')

# Create your models here.

class course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=10)
    course_created_date = models.DateField(auto_now_add=True)
    course_updated_date = models.DateField(auto_now=True)
    

    def __str__(self):
        return self.course_name
    
class session_year(models.Model):
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    

    def __str__(self):
        return str(self.session_start_year) + " - " + str(self.session_end_year)
    

class staff(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.DO_NOTHING)
    address = models.TextField()
    gender = models.CharField(max_length=10)
    phone_number = models.TextField()
    
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return str(self.admin.first_name) + " " + str(self.admin.last_name)

class student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.DO_NOTHING)
    address = models.TextField()
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15, default='')
    course_id = models.ForeignKey(course, on_delete=models.DO_NOTHING)
    session_year_id = models.ForeignKey(session_year, on_delete=models.DO_NOTHING)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


    def __str__(self):
        return str(self.admin.first_name) + " " + str(self.admin.last_name)

class subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10)
    course_id = models.ForeignKey(course, on_delete=models.CASCADE)
    staff_id = models.ForeignKey(staff, on_delete=models.CASCADE)
    
    created_at = models.DateField(auto_now_add=True,null=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return str(self.subject_name) + " - " + str(self.course_id)

class staff_notification(models.Model):
    staff_id = models.ForeignKey(staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True,default=0)
    
    def __str__(self):
        return str(self.staff_id.admin.first_name) 
    
class LeaveType(models.Model):
    name = models.CharField(max_length=50, default='General Leave')

    def __str__(self):
        return self.name
    
class staff_leave(models.Model):
    staff_id = models.ForeignKey(staff, on_delete=models.CASCADE)
    leave_start_date = models.DateField()
    leave_end_date = models.DateField()
    leave_message = models.TextField()
    leave_status = models.IntegerField(null=True,default=0)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return str(self.staff_id.admin.first_name) + " " + str(self.leave_start_date) + " - " + str(self.leave_end_date)
    


class student_notification(models.Model):
    student_id = models.ForeignKey(student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(null=True,default=0)
    
    def __str__(self):
        return str(self.student_id.admin.first_name) 

class staff_feedback(models.Model):   
    staff_id = models.ForeignKey(staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.staff_id.admin.first_name + " " + self.staff_id.admin.last_name


class student_leave(models.Model):
    student_id = models.ForeignKey(student, on_delete=models.CASCADE)
    leave_start_date = models.DateField()
    leave_end_date = models.DateField()
    leave_message = models.TextField()
    leave_status = models.IntegerField(null=True,default=0)

    def __str__(self):
        return str(self.student_id.admin.first_name) + " " + str(self.leave_start_date) + " - " + str(self.leave_end_date)

class student_feedback(models.Model):   
    student_id = models.ForeignKey(student, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField(blank=True)

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):

        return str(self.student_id.admin.first_name) + " " + str(self.student_id.admin.last_name)
    
class attendance(models.Model):
    subject_id = models.ForeignKey(subject, on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    session_year_id = models.ForeignKey(session_year, on_delete=models.DO_NOTHING)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return str(self.subject_id.subject_name) + " - " + str(self.attendance_date) + " - " + str(self.session_year_id.session_start_year) + " - " + str(self.session_year_id.session_end_year)
    
class attendance_report(models.Model):
    attendance_id = models.ForeignKey(attendance, on_delete=models.CASCADE)
    student_id = models.ForeignKey(student, on_delete=models.DO_NOTHING)
    is_present = models.BooleanField(default=True)   # <-- Added field
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.student_id.admin.first_name} {self.student_id.admin.last_name} - {'Present' if self.is_present else 'Absent'}"

    
class result(models.Model):
    student_id = models.ForeignKey(student, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(subject, on_delete=models.CASCADE)
    assignment_marks = models.IntegerField()
    assessment_marks = models.IntegerField()
    ut_marks = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self):
        return str(self.student_id.admin.first_name) + " " + str(self.subject_id.subject_name) 



# Time Table

DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
]

class TimeTable(models.Model):
    staff = models.ForeignKey(staff, on_delete=models.CASCADE)
    subject = models.ForeignKey(subject, on_delete=models.CASCADE)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    session_year = models.ForeignKey(session_year, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.subject.subject_name} ({self.day})"