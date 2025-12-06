from django.shortcuts import render, redirect
from app.models import TimeTable,staff, course, subject, student,CustomUser,result,staff_leave,staff_notification,staff_feedback,session_year,attendance,attendance_report,LeaveType
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime

@login_required(login_url='/')
def Staff_home(request):
    staff_obj = staff.objects.get(admin=request.user)

    # Get subjects assigned to the staff
    assigned_subjects = subject.objects.filter(staff_id=staff_obj)

    # Get notifications for the staff
    notification_obj = staff_notification.objects.filter(staff_id=staff_obj.id).order_by('-id')

    context = {
        'staff_obj': staff_obj,
        'assigned_subjects': assigned_subjects,
        'notification_obj': notification_obj,
    }

    return render(request, 'Staff/home.html', context)

@login_required(login_url='/')
def Staff_notification(request):
    staff_obj = staff.objects.filter(admin=request.user.id)
    for i in staff_obj:
        staff_id =i.id
    staff_notification_obj = staff_notification.objects.filter(staff_id=staff_id)
    context = {
        'staff_notification_obj': staff_notification_obj,
    }
    return render(request, 'Staff/staff_notification.html',context)

@login_required(login_url='/')
def Staff_mark_as_done(request,status):
    notificaion_obj = staff_notification.objects.get(id=status)
    notificaion_obj.status = 1

    notificaion_obj.save()
    return redirect('staff_notification')

@login_required(login_url='/')
def Staff_apply_leave(request):
    staff_obj = staff.objects.filter(admin=request.user.id)
    for i in staff_obj:
        staff_id = i.id

    staff_leave_obj = staff_leave.objects.filter(staff_id=staff_id)

    leave_types = LeaveType.objects.all()  # get all leave types

    context = {
        'staff_leave_obj': staff_leave_obj,
        'leave_types': leave_types,  # pass to template
    }
    return render(request, 'Staff/apply_leave.html', context)




@login_required(login_url='/')
def Staff_apply_leave_save(request):
    if request.method == 'POST':
        leave_start_date_str = request.POST.get('leave_start_date')
        leave_end_date_str = request.POST.get('leave_end_date')
        reason = request.POST.get('reason', '').strip()
        leave_type_id = request.POST.get('leave_type')

        # Basic validations
        if not leave_start_date_str or not leave_end_date_str or not reason or not leave_type_id:
            messages.error(request, "All fields are required.")
            return redirect('staff_apply_leave')

        try:
            leave_start_date = datetime.strptime(leave_start_date_str, '%Y-%m-%d').date()
            leave_end_date = datetime.strptime(leave_end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('staff_apply_leave')

        if leave_start_date > leave_end_date:
            messages.error(request, "Leave start date cannot be after end date.")
            return redirect('staff_apply_leave')

        duration_days = (leave_end_date - leave_start_date).days + 1  # inclusive of both days
        if duration_days > 30:
            messages.error(request, "You can only apply for leave up to 30 days.")
            return redirect('staff_apply_leave')

        try:
            staff_obj = staff.objects.get(admin=request.user.id)
        except staff.DoesNotExist:
            messages.error(request, "Staff profile not found.")
            return redirect('staff_apply_leave')

        try:
            leave_type_obj = LeaveType.objects.get(id=leave_type_id)
        except LeaveType.DoesNotExist:
            messages.error(request, "Selected leave type does not exist.")
            return redirect('staff_apply_leave')

        # Save the leave request
        staff_leave_obj = staff_leave(
            staff_id=staff_obj,
            leave_start_date=leave_start_date,
            leave_end_date=leave_end_date,
            leave_message=reason,
            leave_type=leave_type_obj,
        )
        staff_leave_obj.save()
        messages.success(request, "Leave applied successfully")
        return redirect('staff_apply_leave')

    return redirect('staff_apply_leave')



@login_required(login_url='/')
def Staff_feedback(request ):

    staff_id= staff.objects.get(admin=request.user.id)
    feedback_history = staff_feedback.objects.filter(staff_id=staff_id)
    context = {
        'feedback_history': feedback_history,
    }
    return render(request, 'Staff/feedback.html',context)



def Staff_feedback_save(request):
    if request.method == "POST":
        feedback = request.POST.get('feedback')
        staff_id = staff.objects.get(admin=request.user.id)  # Declare here or earlier in the function

        feedback= staff_feedback(
            staff_id=staff_id,
            feedback=feedback,
            feedback_reply="",
        )
        feedback.save()

        messages.success(request, "Feedback submitted successfully")
        return redirect('staff_feedback')  # Redirect to the correct URL if necessary

def take_attendance(request):
    staff_obj = staff.objects.filter(admin=request.user.id)
    subject_obj = subject.objects.filter(staff_id__in=staff_obj)
    session_year_obj = session_year.objects.all()
    action = request.GET.get('action')

    get_subject = None
    get_session = None
    student_obj = None
    if action is not None:
        if request.method == 'POST':
            subject_id = request.POST.get('subject_id')
            session_id = request.POST.get('session_id')

            get_subject = subject.objects.get(id=subject_id)
            get_session = session_year.objects.get(id=session_id)

            subject_obj = subject.objects.filter(id=subject_id)
            for i in subject_obj:
                student_id = i.course_id.id
                student_obj = student.objects.filter(course_id=student_id)  

            
    context = {
        'staff_obj': staff_obj,
        'subject_obj': subject_obj,
        'session_year_obj': session_year_obj,
        'get_subject':get_subject,
        'get_session':get_session,
        'action': action,
        'student_obj': student_obj
    }

    return render(request, 'Staff/take_attendance.html',context)

def save_attendance(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        session_id = request.POST.get('session_id')
        attendance_date = request.POST.get('attendance_date')
        student_id = request.POST.getlist('students')

        get_subject = subject.objects.get(id=subject_id)
        get_session = session_year.objects.get(id=session_id)

        attendance_obj = attendance(
            subject_id=get_subject,
            session_year_id=get_session,
            attendance_date=attendance_date
        )
        attendance_obj.save()

        for i in student_id:
            stud_id = i 
            int_stud = int(stud_id)
            p_students = student.objects.get(id=int_stud)

            attendance_report_obj = attendance_report(
                attendance_id=attendance_obj,
                student_id=p_students,
            )
            attendance_report_obj.save()  

        messages.success(request, "Attendance saved successfully")
        return redirect('take_attendance')

    return None

def view_attendance(request):
    staff_obj = staff.objects.filter(admin=request.user.id)
    subject_obj = subject.objects.filter(staff_id__in=staff_obj)
    session_year_obj = session_year.objects.all()
    action = request.GET.get('action')

    get_subject = None
    get_session = None
    attendance_date = None
    student_status_list = []

    if action is not None and request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        session_id = request.POST.get('session_id')
        attendance_date = request.POST.get('attendance_date')

        get_subject = subject.objects.get(id=subject_id)
        get_session = session_year.objects.get(id=session_id)

        attendance_qs = attendance.objects.filter(
            subject_id=get_subject,
            session_year_id=get_session,
            attendance_date=attendance_date
        )

        students = student.objects.filter(
            course_id=get_subject.course_id,
            session_year_id=get_session
        )

        for stu in students:
            status = "Absent"
            for att in attendance_qs:
                report = attendance_report.objects.filter(
                    attendance_id=att,
                    student_id=stu
                ).first()
                if report:
                    status = "Present" if report.is_present else "Absent"
                    break  # No need to check more if found
            student_status_list.append({
                'student': stu,
                'status': status
            })

    context = {
        'subject_obj': subject_obj,
        'session_year_obj': session_year_obj,
        'action': action,
        'get_subject': get_subject,
        'get_session': get_session,
        'attendance_date': attendance_date,
        'student_status_list': student_status_list
    }
    return render(request, 'Staff/view_attendance.html', context)




def add_result(request):
    staff_obj = staff.objects.filter(admin=request.user.id)
    subject_obj = subject.objects.filter(staff_id__in=staff_obj)
    session_year_obj = session_year.objects.all()
    action = request.GET.get('action')
    get_subject = None
    get_session = None
    student_obj = None
    results = None  # For existing results to show in the table
    
    if action == 'get_student' and request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        session_id = request.POST.get('session_id')

        if not subject_id or not session_id:
            messages.error(request, "Please select both subject and session year")
            return redirect('add_result')

        get_subject = subject.objects.get(id=subject_id)
        get_session = session_year.objects.get(id=session_id)

        subject_obj = subject.objects.filter(id=subject_id)
        # Get course id from subject
        course_id = get_subject.course_id.id

        # Filter students by course and session
        student_obj = student.objects.filter(course_id=course_id, session_year_id=session_id)

        # Get existing results for this subject and session
        results = result.objects.filter(subject_id=get_subject, student_id__in=student_obj)

    context = {
        'subject_obj': subject_obj,
        'session_year_obj': session_year_obj,
        'action': action,
        'get_subject': get_subject,
        'get_session': get_session,
        'student_obj': student_obj,
        'results': results,
    }

    return render(request, 'Staff/add_result.html', context)


def save_result(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        session_id = request.POST.get('session_id')
        student_id = request.POST.get('student_id')
        assessment_marks = request.POST.get('assessment_marks')
        ut_marks = request.POST.get('UT_marks')
        assignment_marks = request.POST.get('assignment_marks')

        # Validate input presence
        if not all([subject_id, session_id, student_id, assessment_marks, ut_marks, assignment_marks]):
            messages.error(request, "Please fill all required fields.")
            return redirect('add_result')

        get_subject = subject.objects.get(id=subject_id)
        get_student = student.objects.get(id=student_id)

        # Check if result already exists for this student & subject
        check_exists = result.objects.filter(
            subject_id=get_subject,
            student_id=get_student
        ).exists()

        if check_exists:
            result_obj = result.objects.get(
                subject_id=get_subject,
                student_id=get_student
            )
            result_obj.assignment_marks = assignment_marks
            result_obj.assessment_marks = assessment_marks
            result_obj.ut_marks = ut_marks
            result_obj.save()
            messages.success(request, "Result updated successfully")
        else:
            result_obj = result(
                student_id=get_student,
                subject_id=get_subject,
                assignment_marks=assignment_marks,
                assessment_marks=assessment_marks,
                ut_marks=ut_marks
            )
            result_obj.save()
            messages.success(request, "Result saved successfully")

        return redirect('add_result')

    return redirect('add_result')



def staff_view_timetable(request):
    try:
        staff_obj = staff.objects.get(admin=request.user.id)
        timetable = TimeTable.objects.filter(staff=staff_obj).order_by('day', 'start_time')
    except staff.DoesNotExist:
        timetable = []
    return render(request, 'Staff/view_timetable.html', {'timetable': timetable})
