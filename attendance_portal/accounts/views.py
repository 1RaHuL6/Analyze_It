from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm
from django.contrib import messages
from .forms import StaffUserRegistrationForm
from django.contrib.auth.models import User
from analytics.views import dashboard  

#admin
#admin

#user
#user


def user_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('analytics:dashboard')  
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def register_user(request):
    if request.method == 'POST':
        form = StaffUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True  # Make sure they can log in
            user.save()
            messages.success(request, 'New staff user registered successfully.')
            return redirect('analytics:dashboard')
    else:
        form = StaffUserRegistrationForm()
    return render(request, 'register.html', {'form': form})



