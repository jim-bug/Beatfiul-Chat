import json, random, html, datetime
from django.shortcuts import render, redirect
from django.core.handlers.asgi import ASGIRequest
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import JsonResponse
from beautiful_chat.models import Chat, UserProfile, Message
from .websockets import send_message_to_chat

# Handle /
def index(request):
    return render(request, 'index.html')

# Handle /chats/ and /chats/<chat_id>/
@login_required
def chats(request: ASGIRequest, chat_id = None):
    if(request.method == 'POST' and chat_id is None):
        return new_chat(request)
    
    chats = Chat.objects.all()
    # order chats by the most recently updated
    chats = sorted(chats, key=lambda chat: chat.updated_at, reverse=True)
    profile = UserProfile.objects.get(user=request.user)

    # if chat_id is not None, redirect to the chat page
    if chat_id is not None:
        chat = Chat.objects.filter(chat_id=chat_id).first()
        if chat is None:
            return render(request, 'chats.html', {'chats': chats, 'profile': profile})
        messages = Message.objects.filter(chat=chat)
        return render(request, 'chats.html', {'chats': chats, 'chat_id': chat_id,
                'messages': messages, 'profile': profile})
    # main chats page
    return render(request, 'chats.html', {'chats': chats, 'profile': profile})

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


@login_required
def message_handler(request: ASGIRequest, chat_id: str):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        message = data.get('message')
        if message is None or message.strip() == '':
            return JsonResponse({'error': 'message is required'}, status=400)
        # sanitize the message to prevent XSS
        message = html.escape(message)
        if len(message) > 2000:
            return JsonResponse({'error': 'message must be less than 2000 characters'}, status=400)
        # send the message to the connected clients
        event = {
            'text': message,
            'user': request.user.username,
            'created_at': datetime.datetime.now().isoformat()
        }
        chat = Chat.objects.get(chat_id=chat_id)
        msg = Message(chat=chat, text=message, user=request.user.username)
        send_message_to_chat(chat_id, event)
        msg.save()
        chat.save()
        return JsonResponse({'success': True})
    elif request.method == 'GET':
        chat = Chat.objects.get(chat_id=chat_id)
        messages = list(Message.objects.filter(chat=chat).values())
        return JsonResponse({'messages': messages})
