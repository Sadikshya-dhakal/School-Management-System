from django.shortcuts import render, redirect, HttpResponse
from app.EmailBackEnd import EmailBackend
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout 
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from app.models import CustomUser

def base(request):
    return render(request, 'base.html')

def login_view(request):  
    return render(request, 'login.html')

def doLogin(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('user_role')
        
        user = EmailBackend.authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if selected role matches user's actual role
            if str(user.user_type) != selected_role:
                messages.error(request, 'Invalid role selection for this account')
                return redirect('login')
            
            auth_login(request, user)  
            user_type = user.user_type
            if user_type == '1':
                return redirect('home')  # Redirect to HOD home page
            elif user_type == '2':
                return redirect('staff_home')  # Redirect to staff home page
            elif user_type == '3':
                return redirect('student_home')
            else:
                messages.error(request, 'Invalid user type')
                return redirect('login')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

def doLogout(request):
    auth_logout(request)
    return redirect('login')


def profile(request):
    user=CustomUser.objects.get(id = request.user.id)

    context={
        "user":user,
    }
    return render(request, 'profile.html',context)

def profile_update(request):
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        print(profile_pic, first_name, last_name, password)
        try:
            user = CustomUser.objects.get(id=request.user.id)
            user.first_name = first_name
            user.last_name = last_name
            if profile_pic:
                user.profile_pic = profile_pic
            if password and password.strip() != "":
                user.set_password(password)
            user.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Failed to update profile! Error: {str(e)}')
            return redirect('profile')

    return render(request, 'profile.html')
