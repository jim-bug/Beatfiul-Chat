import json, random
from django.shortcuts import render, redirect
from django.core.handlers.asgi import ASGIRequest
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from beautiful_chat.models import Chat

# Handle /
def index(request):
    return render(request, 'index.html')

# Handle /chats/ and /chats/<chat_id>/
@login_required
def chats(request: ASGIRequest, chat_id = None):
    if(request.method == 'POST' and chat_id is None):
        return new_chat(request)
    if chat_id is not None:
        # TODO
        return JsonResponse({'error': 'Not implemented'}, status=501)
    chats = Chat.objects.all()
    # order chats by the most recently updated
    chats = sorted(chats, key=lambda chat: chat.updated_at, reverse=True)
    return render(request, 'chats.html', {'chats': chats})

@login_required
def new_chat(request: ASGIRequest):
    # get the chat name from the form
    data = request.body.decode('utf-8')
    data = json.loads(data)
    chat_name = data.get('chat_name')
    if chat_name is None:
        return JsonResponse({'error': 'chat_name is required'}, status=400)
    if len(chat_name) > 200:
        return JsonResponse({'error': 'chat_name must be less than 200 characters'}, status=400)
    # create a new chat
    chat_id = random.randbytes(16).hex()
    chat = Chat(name=chat_name, chat_id=chat_id, owner=request.user.username)
    chat.save()
    # redirect to the new chat
    return redirect(f'/chats/{chat_id}/')

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