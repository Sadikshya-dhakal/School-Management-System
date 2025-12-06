from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction

import re
import os
import pandas as pd
import json
from app.models import TimeTable,course, session_year, result,staff_leave,student,CustomUser,staff,subject,staff_notification,staff_feedback,student_notification,student_feedback,student_leave,attendance, attendance_report,LeaveType
from django.contrib import messages
from django.shortcuts import get_object_or_404



@login_required(login_url='/')
def home(request):
    student_count = student.objects.all().count()
    staff_count = staff.objects.all().count()
    course_count = course.objects.all().count()
    subject_count = subject.objects.all().count()
    male_student_count = student.objects.filter(gender='Male').count()
    female_student_count = student.objects.filter(gender='Female').count()

    # 👇 Add student details
    all_students = student.objects.select_related('course_id').all()
    if student_count > 0:
        male_percentage = round(male_student_count / student_count * 100, 2)
        female_percentage = round(female_student_count / student_count * 100, 2)
    else:
        male_percentage = 0
        female_percentage = 0

    context = {
        'student_count': student_count,
        'staff_count': staff_count,
        'course_count': course_count,
        'subject_count': subject_count,
        'male_student_count': male_student_count,
        'female_student_count': female_student_count,
        'all_students': all_students,  # 👈 Include this
        'male_percentage':male_percentage,
        'female_percentage':female_percentage,
    }

    return render(request, 'Hod/home.html', context)


@login_required(login_url='/')
def myprofile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'Hod/myprofile.html', context)

NAME_REGEX = re.compile(r'^[A-Za-z]')

ALLOWED_IMAGE_MIME = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

@login_required(login_url='/')
def add_student(request):
    courses = course.objects.all()
    session_years = session_year.objects.all()

    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        email = (request.POST.get('email') or '').lower().strip()
        username = (request.POST.get('username') or '').lower().strip()
        password = request.POST.get('password') or ''
        phone_number = request.POST.get('phone_number') or ''
        address = request.POST.get('address') or ''
        gender = request.POST.get('gender') or ''
        selected_course_id = request.POST.get('course')
        selected_session_year_id = request.POST.get('session_year')

        # Basic validations
        if not first_name or not NAME_REGEX.match(first_name):
            messages.error(request, 'First name must start with an alphabet letter.')
            return redirect('add_student')

        if not last_name or not NAME_REGEX.match(last_name):
            messages.error(request, 'Last name  must start with an alphabet letter.')
            return redirect('add_student')

        if not email:
            messages.error(request, 'Email is required.')
            return redirect('add_student')

        if not username:
            messages.error(request, 'Username is required.')
            return redirect('add_student')

        if not password:
            messages.error(request, 'Password is required.')
            return redirect('add_student')

        if not selected_course_id or not selected_session_year_id:
            messages.error(request, 'Course and Session Year must be selected.')
            return redirect('add_student')

        # Unique checks
        if CustomUser.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('add_student')

        if CustomUser.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('add_student')

        # Profile pic validation
        if profile_pic:
            content_type = getattr(profile_pic, 'content_type', '')
            name_lower = profile_pic.name.lower()
            ext = '.' + name_lower.split('.')[-1] if '.' in name_lower else ''
            if content_type not in ALLOWED_IMAGE_MIME or ext not in ALLOWED_EXT:
                messages.error(request, 'Profile picture must be an image (JPEG, PNG, GIF, WEBP).')
                return redirect('add_student')
            if profile_pic.size > MAX_IMAGE_SIZE:
                messages.error(request, 'Profile picture must be smaller than 5MB.')
                return redirect('add_student')
        else:
            messages.error(request, 'Profile picture is required.')
            return redirect('add_student')

        # At this point all validations passed; proceed to create
        try:
            with transaction.atomic():
                user = CustomUser(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    profile_pic=profile_pic,
                    user_type=3,
                )
                user.set_password(password)
                user.save()

                # Fetch related objects; if invalid ID, these will throw.
                selected_course = course.objects.get(id=selected_course_id)
                selected_session_year = session_year.objects.get(id=selected_session_year_id)

                students = student(
                    admin=user,
                    address=address,
                    phone_number=phone_number,
                    gender=gender,
                    course_id=selected_course,
                    session_year_id=selected_session_year
                )
                students.save()

            messages.success(request, 'Student added successfully.')
            return redirect('add_student')
        except course.DoesNotExist:
            messages.error(request, 'Selected course does not exist.')
        except session_year.DoesNotExist:
            messages.error(request, 'Selected session year does not exist.')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

        return redirect('add_student')

    context = {
        'courses': courses,
        'session_years': session_years,
    }
    return render(request, 'Hod/add_student.html', context)



@login_required(login_url='/')
def VIEW_STUDENT(request):
    students = student.objects.all()
    context = {
        'students': students,
    }
    return render(request, 'Hod/view_student.html', context)
@login_required(login_url='/')
def edit_student(request,id):
    student_id = student.objects.get(id=id)
    courses = course.objects.all()
    session_years = session_year.objects.all()
    context = {
        'student': student_id,
        'courses': courses,
        'session_years': session_years,
    }
    return render(request, 'Hod/edit_student.html',context)
@login_required(login_url='/')
def update_student(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password') 
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        gender = request.POST.get('gender') 
        selected_course_id = request.POST.get('course')  
        selected_session_year_id = request.POST.get('session_year')

        student_obj = student.objects.get(id=student_id)
        user = CustomUser.objects.get(id=student_obj.admin.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username

        if password:  # Only update if a new password is provided
            user.set_password(password)

        if profile_pic:  # Only update if a new profile picture is uploaded
            user.profile_pic = profile_pic

        user.save()

        student_obj.address = address
        student_obj.phone_number = phone_number
        student_obj.gender = gender
        student_obj.course_id = course.objects.get(id=selected_course_id)
        student_obj.session_year_id = session_year.objects.get(id=selected_session_year_id)
        student_obj.save()

        messages.success(request, 'Student updated successfully')
        return redirect('view_student')

    return render(request, 'Hod/edit_student.html')


@login_required(login_url='/')
def delete_student(request, admin):
    user = CustomUser.objects.get(id=admin)
    try:
        # Delete the related student object first
        student_obj = student.objects.get(admin=user)
        student_obj.delete()
        # Then delete the user
        user.delete()
        messages.success(request, 'Student deleted successfully')
    except student.DoesNotExist:
        messages.error(request, 'Student record not found')
    except Exception as e:
        messages.error(request, f'Error occurred: {str(e)}')
    return redirect('view_student')

@login_required(login_url='/')
def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_code = request.POST.get('course_code')

        # Check if the course already exists
        if course.objects.filter(course_name__iexact=course_name).exists():
            messages.error(request, 'Course with this name already exists')
            return redirect('add_course')

        if course.objects.filter(course_code__iexact=course_code).exists():
            messages.error(request, 'Course with this code already exists')
            return redirect('add_course')

        if not course_code:
            messages.error(request, 'Course code is required')
            return redirect('add_course')

        course_obj = course(
            course_name=course_name,
            course_code=course_code
        )
        course_obj.save()
        messages.success(request, 'Course added successfully')
        return redirect('add_course')
    context = {}    
    return render(request, 'Hod/add_course.html', context)
@login_required(login_url='/')
def view_course(request):
    courses = course.objects.all()
    context = {
        'courses': courses,
    }
    return render(request, 'Hod/view_course.html', context)



@login_required(login_url='/')
def edit_course(request,id):
    course_id = course.objects.get(id=id)
    context = {
        'course': course_id,
    }
    return render(request, 'Hod/edit_course.html',context)
@login_required(login_url='/')
def update_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course_name')
        course_code = request.POST.get('course_code')

        course_obj = course.objects.get(id=course_id)
        course_obj.course_name = course_name
        course_obj.course_code = course_code
        course_obj.save()
        messages.success(request, 'Course updated successfully')
        return redirect('view_course')

    return render(request, 'Hod/edit_course.html')
@login_required(login_url='/')
def delete_course(request, id):
    course_obj = course.objects.get(id=id)
    course_obj.delete()
    messages.success(request, 'Course deleted successfully')
    return redirect('view_course')



NAME_REGEX = re.compile(r'^[A-Za-z]')
ALLOWED_IMAGE_MIME = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

@login_required(login_url='/')
def add_staff(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        email = (request.POST.get('email') or '').lower().strip()
        username = (request.POST.get('username') or '').lower().strip()
        password = request.POST.get('password') or ''
        phone_number = (request.POST.get('phone_number') or '').strip()
        address = (request.POST.get('address') or '').strip()
        gender = request.POST.get('gender') or ''

        # Validate names
        if not first_name or not NAME_REGEX.match(first_name):
            messages.error(request, 'First name is required and must start with an alphabet letter.')
            return redirect('add_staff')
        if not last_name or not NAME_REGEX.match(last_name):
            messages.error(request, 'Last name is required and must start with an alphabet letter.')
            return redirect('add_staff')

        # Required fields
        if not email:
            messages.error(request, 'Email is required.')
            return redirect('add_staff')
        if not username:
            messages.error(request, 'Username is required.')
            return redirect('add_staff')
        if not password:
            messages.error(request, 'Password is required.')
            return redirect('add_staff')

        # Unique checks
        if CustomUser.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('add_staff')
        if CustomUser.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('add_staff')

        # Profile pic validation
        if profile_pic:
            content_type = getattr(profile_pic, 'content_type', '')
            name_lower = profile_pic.name.lower()
            ext = '.' + name_lower.split('.')[-1] if '.' in name_lower and '.' in profile_pic.name else ''
            if content_type not in ALLOWED_IMAGE_MIME or ext not in ALLOWED_EXT:
                messages.error(request, 'Profile picture must be an image (JPEG, PNG, GIF, WEBP).')
                return redirect('add_staff')
            if profile_pic.size > MAX_IMAGE_SIZE:
                messages.error(request, 'Profile picture must be smaller than 5MB.')
                return redirect('add_staff')
        else:
            messages.error(request, 'Profile picture is required.')
            return redirect('add_staff')

        # All validations passed; create user and staff
        try:
            with transaction.atomic():
                user = CustomUser(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    profile_pic=profile_pic,
                    user_type=2,  # assuming 2 is staff
                )
                user.set_password(password)
                user.save()

                staff_obj = staff(
                    admin=user,
                    address=address,
                    phone_number=phone_number,
                    gender=gender
                )
                staff_obj.save()

            messages.success(request, 'Staff added successfully.')
            return redirect('add_staff')
        except Exception as e:
            messages.error(request, f'Unexpected error: {str(e)}')
            return redirect('add_staff')

    return render(request, 'Hod/add_staff.html')


@login_required(login_url='/')
def view_staff(request):
    staff_members = staff.objects.all()
    context = {
        'staff_members': staff_members,
    }

    return render(request, 'Hod/view_staff.html',context)


@login_required(login_url='/')
def edit_staff(request,id):
    staff_id = staff.objects.get(id=id)
    context = {
        'staff': staff_id,
    }
    return render(request, 'Hod/edit_staff.html',context)
@login_required(login_url='/')
def update_staff(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password') 
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        staff_obj = staff.objects.get(id=staff_id)
        user=CustomUser.objects.get(id=staff_obj.admin.id)
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        
        if password != " ":
            user.set_password(password)
        if profile_pic != " ":
            user.profile_pic = profile_pic

        user.save()

        staff_obj = staff.objects.get(id=staff_id)
        staff_obj.address = address
        staff_obj.phone_number = phone_number
        staff_obj.gender=gender

        staff_obj.save()
        messages.success(request, 'Staff updated successfully')
        return redirect('view_staff')
    return render(request, 'Hod/edit_staff.html')

@login_required(login_url='/')
def delete_staff(request, admin):
    user = CustomUser.objects.get(id=admin)
    try:
        # Delete the related staff object first
        staff_obj = staff.objects.get(admin=user)
        staff_obj.delete()
        # Then delete the user
        user.delete()
        messages.success(request, 'Staff deleted successfully')
    except staff.DoesNotExist:
        messages.error(request, 'Staff record not found')
    except Exception as e:
        messages.error(request, f'Error occurred: {str(e)}')
    return redirect('view_staff')

@login_required(login_url='/')
def add_subject(request):
    courses = course.objects.all()
    staff_members = staff.objects.all()

    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        selected_course_id = request.POST.get('course_id')  
        selected_staff_id = request.POST.get('staff_id')

        
        course_obj = course.objects.get(id=selected_course_id)
        staff_obj = staff.objects.get(id=selected_staff_id)

        subject_obj = subject(
            subject_name=subject_name,
            subject_code=subject_code,
            course_id=course_obj,
            staff_id=staff_obj
        )
        subject_obj.save()
        messages.success(request, 'Subject added successfully')
        return redirect('add_subject')

    context = {
        'courses': courses,
        'staff_members': staff_members,
    }
    return render(request, 'Hod/add_subject.html', context)
@login_required(login_url='/')
def view_subject(request):

    subject_obj = subject.objects.all()
    context = {
        'subject_obj': subject_obj,
    }
    return render(request, 'Hod/view_subject.html',context)
@login_required(login_url='/')
def edit_subject(request,id):
    subject_id = subject.objects.get(id=id)
    courses = course.objects.all()
    staff_members = staff.objects.all()
    context = {
        'subject': subject_id,
        'courses': courses,
        'staff_members': staff_members,
    }
    return render(request, 'Hod/edit_subject.html',context)
@login_required(login_url='/')
def update_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        selected_course_id = request.POST.get('course_id')
        selected_staff_id = request.POST.get('staff_id')

        course_obj = course.objects.get(id=selected_course_id)
        staff_obj = staff.objects.get(id=selected_staff_id)

        subject_obj = subject(
            id=subject_id,
            subject_name=subject_name,
            subject_code=subject_code,
            course_id=course_obj,
            staff_id=staff_obj

        )
        subject_obj.save()
        messages.success(request, 'Subject updated successfully')
        
    return redirect('view_subject')
@login_required(login_url='/')
def delete_subject(request, id):
    subject_obj = subject.objects.get(id=id)
    subject_obj.delete()    
    messages.success(request, 'Subject deleted successfully')
    return redirect('view_subject')

@login_required(login_url='/')
def add_session(request):
    if request.method == 'POST':
        session_start_year = request.POST.get('start_date')
        session_end_year = request.POST.get('end_date')

        # Check if the session year already exists
        if session_year.objects.filter(session_start_year=session_start_year, session_end_year=session_end_year).exists():
            messages.error(request, 'Session year already exists')
            return redirect('add_session')

        session_obj = session_year(
            session_start_year=session_start_year,
            session_end_year=session_end_year
        )
        session_obj.save()
        messages.success(request, 'Session year added successfully')
        return redirect('add_session')
    return render(request, 'Hod/add_session.html')

@login_required(login_url='/')
def view_session(request):
    session_years = session_year.objects.all()
    context = {
        'session_years': session_years,
    }
    return render(request, 'Hod/view_session.html', context)

@login_required(login_url='/')
def edit_session(request,id):
    session_obj = session_year.objects.get(id=id)
    context = {
        'session': session_obj,
    }
    return render(request, 'Hod/edit_session.html',context)
@login_required(login_url='/')
def update_session(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('start_date')
        session_end_year = request.POST.get('end_date')

        session_obj = session_year.objects.get(id=session_id)
        session_obj.session_start_year = session_start_year
        session_obj.session_end_year = session_end_year
        session_obj.save()
        messages.success(request, 'Session updated successfully')
        return redirect('view_session')

    return render(request, 'Hod/edit_session.html')
@login_required(login_url='/')
def delete_session(request, id):
    session_obj = session_year.objects.get(id=id)
    session_obj.delete()
    messages.success(request, 'Session deleted successfully')
    return redirect('view_session')
@login_required(login_url='/')
def send_staff_notification(request):
    staff_members = staff.objects.all()
    see_notification = staff_notification.objects.all().order_by('-id')[0:5]
    context = {
        'staff_members': staff_members,
        'see_notification': see_notification,
    }
    
    return render(request, 'Hod/send_staff_notification.html',context)

@login_required(login_url='/')
def save_staff_notification(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        message = request.POST.get('message')

        staff_obj = staff.objects.get(admin=staff_id)
        notification =staff_notification(
            staff_id=staff_obj,
            message=message
        )

        # Save the notification to the user's profile
        
        notification.save()

        messages.success(request, 'Notification sent successfully')
        return redirect('send_staff_notification')

    return render(request, 'Hod/send_staff_notification.html')
@login_required(login_url='/')   
def view_staff_leave(request):
    staff_leave_obj = staff_leave.objects.all()
    context = {
        'staff_leave_obj': staff_leave_obj,
    }
    return render(request, 'Hod/view_staff_leave.html',context)


@login_required(login_url='/')
def add_leave_type(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            LeaveType.objects.create(name=name)
            messages.success(request, "Leave type added successfully")
        return redirect('add_leave_type')
    
    leave_types = LeaveType.objects.all()
    return render(request, 'HOD/add_leave_type.html', {'leave_types': leave_types})

@login_required(login_url='/')
def delete_leave_type(request, id):
    LeaveType.objects.filter(id=id).delete()
    messages.success(request, "Leave type deleted")
    return redirect('add_leave_type')


@login_required(login_url='/')
def staff_approve_leave(request, id):
    staff_leave_obj = staff_leave.objects.get(id=id)
    staff_leave_obj.leave_status = 1
    staff_leave_obj.save()
    messages.success(request, 'Leave approved successfully')
    return redirect('view_staff_leave')

@login_required(login_url='/')
def staff_disapprove_leave(request, id):
    staff_leave_obj = staff_leave.objects.get(id=id)
    staff_leave_obj.leave_status = 2
    staff_leave_obj.save()
    messages.success(request, 'Leave disapproved successfully')
    return redirect('view_staff_leave')

def views_staff_feedback(request): 
    feedback = staff_feedback.objects.all() 

    context = {
        'feedback': feedback, 
    }
    return render(request, 'Hod/staff_feedback.html', context)

def views_staff_feedback_save(request):
   if request.method == 'POST':
         feedback_id=request.POST.get('feedback_id')
         feedback_reply = request.POST.get('feedback_reply')
         
         
         feedback = staff_feedback.objects.get(id=feedback_id)
         feedback.feedback_reply= feedback_reply
         feedback.save()
         messages.success(request, "Feedback send successfully")
         return redirect('staff_feedback_reply')

@login_required(login_url='/')
def send_student_notification(request):
    students = student.objects.all()
    see_notification = student_notification.objects.all().order_by('-id')[0:5]
    context = {
        'students': students,
        'see_notification': see_notification,
    }
    
    return render(request, 'Hod/send_student_notification.html',context)

@login_required(login_url='/')
def save_student_notification(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        message = request.POST.get('message')

        student_obj = student.objects.get(admin=student_id)
        notification =student_notification(
            student_id=student_obj,
            message=message
        )

        # Save the notification to the user's profile
        
        notification.save()

        messages.success(request, 'Notification sent successfully')
        return redirect('send_student_notification')

    return render(request, 'Hod/send_student_notification.html')

def view_student_leave(request):
    student_leave_obj = student_leave.objects.all()
    context = {
        'student_leave_obj': student_leave_obj,
    }
    return render(request, 'Hod/view_student_leave.html',context)

@login_required(login_url='/')
def student_approve_leave(request, id):
    student_leave_obj = student_leave.objects.get(id=id)
    student_leave_obj.leave_status = 1
    student_leave_obj.save()
    messages.success(request, 'Leave approved successfully')
    return redirect('view_student_leave')

@login_required(login_url='/')
def student_disapprove_leave(request, id):
    student_leave_obj = student_leave.objects.get(id=id)
    student_leave_obj.leave_status = 2
    student_leave_obj.save()
    messages.success(request, 'Leave disapproved successfully')
    return redirect('view_student_leave')


def views_student_feedback(request): 
    feedback = student_feedback.objects.all() 

    context = {
        'feedback': feedback, 
    }
    return render(request, 'Hod/student_feedback.html', context)

def views_student_feedback_save(request):
   if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        feedback_reply = request.POST.get('feedback_reply')

        try:
            feedback = student_feedback.objects.get(id=feedback_id)
            feedback.feedback_reply = feedback_reply
            feedback.save()
            messages.success(request, "Feedback sent successfully.")
        except student_feedback.DoesNotExist:
            messages.error(request, "Feedback not found.")

        return redirect('student_feedback_reply')


def view_attendance(request):
    
    subject_obj = subject.objects.all()
    session_year_obj = session_year.objects.all()
    action = request.GET.get('action')

    get_subject = None
    get_session = None
    attendance_date = None
    attendance_report_obj = None
    if action is not None:
        if request.method == 'POST':
            subject_id = request.POST.get('subject_id')
            session_id = request.POST.get('session_id')
            attendance_date = request.POST.get('attendance_date')

            get_subject = subject.objects.get(id=subject_id)
            get_session = session_year.objects.get(id=session_id)

            attendance_obj = attendance.objects.filter(
                subject_id=get_subject,
                attendance_date=attendance_date,
                session_year_id=get_session,
                
            )
            for i in attendance_obj:
                attendance_id = i.id
                attendance_report_obj = attendance_report.objects.filter(attendance_id=attendance_id)
           

           

    context= {
        'subject_obj': subject_obj,
        'session_year_obj': session_year_obj,
        'action': action,
        'get_subject': get_subject,
        'get_session': get_session,
        'attendance_date': attendance_date,
        'attendance_report_obj': attendance_report_obj ,
    }
    
    return render(request, 'Hod/hod_view_attendance.html',context)

def view_result(request):
    subject_obj = subject.objects.all()
    session_year_obj = session_year.objects.all()
    action = request.GET.get('action')

    get_subject = None
    get_session = None
    student_obj = None
    result_obj = None
    if action is not None:
        if request.method == 'POST':
            subject_id = request.POST.get('subject_id')
            session_id = request.POST.get('session_id')

            get_subject = subject.objects.get(id=subject_id)
            get_session = session_year.objects.get(id=session_id)

            student_obj = student.objects.filter(course_id=get_subject.course_id, session_year_id=get_session)
            result_obj = result.objects.filter(student_id__in=student_obj, subject_id=get_subject)

    context= {
        'subject_obj': subject_obj,
        'session_year_obj': session_year_obj,
        'action': action,
        'get_subject': get_subject,
        'get_session': get_session,
        'student_obj': student_obj,
        'result_obj': result_obj,
    }
    
    return render(request, 'Hod/hod_view_result.html',context)



def add_timetable(request):
    if request.method == "POST":
        staff_id = request.POST.get("staff")
        subject_id = request.POST.get("subject")
        course_id = request.POST.get("course")
        session_id = request.POST.get("session")
        day = request.POST.get("day")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        try:
            timetable = TimeTable(
                staff_id=staff_id,
                subject_id=subject_id,
                course_id=course_id,
                session_year_id=session_id,
                day=day,
                start_time=start_time,
                end_time=end_time
            )
            timetable.save()
            messages.success(request, "Time Table added successfully.")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('add_timetable')

    context = {
        'staffs': staff.objects.all(),
        'subjects': subject.objects.all(),
        'courses': course.objects.all(),
        'sessions': session_year.objects.all(),
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'timetables': TimeTable.objects.all().order_by('day', 'start_time'),
    }
    return render(request, 'Hod/add_timetable.html', context)


def name_valid(s):
    return isinstance(s, str) and s.strip() and s.strip()[0].isalpha()

ALLOWED_EXT = {'.csv', '.xls', '.xlsx'}

import os
import json
import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction

ALLOWED_EXT = ['.csv', '.xlsx']  # your allowed extensions

def bulk_upload_students(request):
    preview_rows = []

    if request.method == 'POST' and 'preview' in request.POST:
        uploaded = request.FILES.get('file')
        if not uploaded:
            messages.error(request, "No file uploaded.")
            return redirect('bulk_upload_students')

        ext = os.path.splitext(uploaded.name)[1].lower()
        if ext not in ALLOWED_EXT:
            messages.error(request, "Unsupported file type.")
            return redirect('bulk_upload_students')

        # Save uploaded file to static/templates folder
        save_dir = os.path.join(settings.BASE_DIR, 'static', 'templates')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, uploaded.name)
        with open(save_path, 'wb+') as destination:
            for chunk in uploaded.chunks():
                destination.write(chunk)

        # Read file into dataframe
        try:
            if ext == '.csv':
                df = pd.read_csv(save_path)
            else:
                df = pd.read_excel(save_path)
        except Exception as e:
            messages.error(request, f"Failed to read file: {str(e)}")
            return redirect('bulk_upload_students')

        required_cols = [
            'first_name', 'last_name', 'email', 'username', 'password',
            'address', 'phone_number', 'gender', 'course_id', 'session_year_id'
        ]
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            messages.error(request, f"Missing required columns: {', '.join(missing)}")
            return redirect('bulk_upload_students')

        for idx, row in df.iterrows():
            first = str(row.get('first_name', '')).strip()
            last = str(row.get('last_name', '')).strip()
            email = str(row.get('email', '')).lower().strip()
            username = str(row.get('username', '')).lower().strip()
            password = str(row.get('password', ''))
            address = str(row.get('address', '')).strip()
            phone = str(row.get('phone_number', '')).strip()
            gender = str(row.get('gender', '')).strip()
            course_id = row.get('course_id')
            session_id = row.get('session_year_id')

            error = None
            course_display = course_id
            session_display = session_id

            try:
                course_obj = course.objects.get(id=course_id)
                course_display = course_obj.course_name
            except Exception:
                error = "Invalid course"

            try:
                session_obj = session_year.objects.get(id=session_id)
                session_display = f"{session_obj.session_start_year}-{session_obj.session_end_year}"
            except Exception:
                error = (error + "; Invalid session") if error else "Invalid session"

            # Add your name_valid() function or replace this check accordingly
            def name_valid(name):
                import re
                return re.match(r'^[A-Za-z]', name) is not None

            if not all([first, last, email, username, password, address, phone, gender, course_id, session_id]):
                error = (error + "; Missing field(s)") if error else "Missing required field(s)"
            if not name_valid(first) or not name_valid(last):
                error = (error + "; Name must start with letter") if error else "Name must start with letter"
            if CustomUser.objects.filter(email__iexact=email).exists():
                error = (error + "; Email exists") if error else "Email exists"
            if CustomUser.objects.filter(username__iexact=username).exists():
                error = (error + "; Username exists") if error else "Username exists"

            row_data = {
                'first_name': first,
                'last_name': last,
                'email': email,
                'username': username,
                'password': password,
                'address': address,
                'phone_number': phone,
                'gender': gender,
                'course_id': course_id,
                'session_year_id': session_id,
                'course_display': course_display,
                'session_display': session_display,
                'error': error,
            }
            row_data['serialized'] = json.dumps(row_data)
            preview_rows.append(row_data)

        request.session['preview_rows'] = [r['serialized'] for r in preview_rows]

    return render(request, 'Hod/bulk_upload_students.html', {
        'preview_rows': preview_rows,
    })


def bulk_upload_confirm(request):
    if request.method != 'POST':
        return redirect('bulk_upload_students')

    serialized_list = request.session.get('preview_rows', [])
    if not serialized_list:
        messages.error(request, "No previewed data to import.")
        return redirect('bulk_upload_students')

    success = 0
    failures = []

    for serialized in serialized_list:
        try:
            row = json.loads(serialized)
        except Exception:
            failures.append("Failed to decode row.")
            continue

        if row.get('error'):
            failures.append(f"Row {row.get('email')}: {row.get('error')}")
            continue

        first = row['first_name']
        last = row['last_name']
        email = row['email']
        username = row['username']
        password = row['password']
        address = row['address']
        phone = row['phone_number']
        gender = row['gender']
        course_id = row['course_id']
        session_id = row['session_year_id']

        try:
            with transaction.atomic():
                user = CustomUser(
                    first_name=first,
                    last_name=last,
                    email=email,
                    username=username,
                    user_type=3,
                )
                user.set_password(password)
                user.save()

                student_obj = student(
                    admin=user,
                    address=address,
                    phone_number=phone,
                    gender=gender,
                    course_id=course.objects.get(id=course_id),
                    session_year_id=session_year.objects.get(id=session_id)
                )
                student_obj.save()
                success += 1
        except Exception as e:
            failures.append(f"{email}: {str(e)}")

    # clear preview session
    request.session.pop('preview_rows', None)

    msg = f"{success} students imported."
    if failures:
        msg += f" {len(failures)} failed."
        for f in failures[:5]:
            messages.error(request, f)
        if len(failures) > 5:
            messages.error(request, f"...and {len(failures)-5} more errors.")
    messages.success(request, msg)
    return redirect('bulk_upload_students')