import json
from django.shortcuts import render, redirect
from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User


# Handle /login/
def loginRoute(request: ASGIRequest):
    if request.method == 'POST':
        # get the username and password from the form
        data = request.body.decode('utf-8')
        data = json.loads(data)
        usernamePost = data.get('username')
        passwordPost = data.get('password')

        if usernamePost is None or passwordPost is None:
            return JsonResponse({'error': 'username and password are required'}, status=400)
        # check if user exists and password is correct
        user = User.objects.filter(username=usernamePost).first()
        if user is None or not user.check_password(passwordPost):
            return JsonResponse({'error': 'invalid username or password'}, status=400)
        # log in the user
        login(request, user)
        # redirect to /chats/
        return redirect('/chats/')
        
    elif request.method == 'GET':
        return render(request, 'login.html')
    
    return JsonResponse({'error': 'Not implemented'}, status=501)

# Handle /logout/
def logoutRoute(request: ASGIRequest):
    logout(request)
    # redirect to the login page
    return redirect('/login/')

# Handle /register/
def register(request: ASGIRequest):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        usernamePost = data.get('username')
        passwordPost = data.get('password')
        if usernamePost is None or passwordPost is None:
            return JsonResponse({'error': 'username and password are required'}, status=400)
        if User.objects.filter(username=usernamePost).exists():
            return JsonResponse({'error': 'username already exists'}, status=400)
        # create a new user
        user = User(username=usernamePost)
        user.set_password(passwordPost)
        user.save()
        # redirect to the login page
        return JsonResponse({'success': True})
    elif request.method == 'GET':
        return render(request, 'register.html')
    
    return JsonResponse({'error': 'Not implemented'}, status=501)

# Handle /profile_picture/ and /profile_picture/<hash>
def profile_picture(request: ASGIRequest, hash = None):
    return JsonResponse({'error': 'Not implemented'}, status=501)