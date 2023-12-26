from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
# Create your views here.

def signup(request):
    return render(request, 'signup.html')

def signin(request):
    return render(request, 'login.html')

@login_required(login_url='signin')
def index(request):
    return render(request, 'index.html')

@login_required(login_url='signin')
def profile(request):
    return render(request, 'profile.html')

def confirmation_page_view(request):
    email = request.GET.get('email')
    return render(request, 'extras/confirmation_page.html', {'email': email})

def invalid_token(request):
    return HttpResponse('invalid-token')

def activation_expired(request):
    return render(request, 'activation_expired.html')

def logout_view(request):
    logout(request)
    return redirect('index')