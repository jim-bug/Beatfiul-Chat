from django.shortcuts import render, redirect
from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.files import File
from beautiful_chat.models import UserProfile
from PIL import Image
from io import BytesIO
import base64
import json


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
        # create a new UserProfile
        profile = UserProfile(user=user)
        profile.save()
        # redirect to the login page
        return JsonResponse({'success': True})
    elif request.method == 'GET':
        return render(request, 'register.html')
    
    return JsonResponse({'error': 'Not implemented'}, status=501)

# Handle /profile/
@login_required
def view_profile(request: ASGIRequest):
    if request.method == 'POST':
        # get the user's profile
        profile = UserProfile.objects.get(user=request.user)
        # get the new username from the form
        data = request.body.decode('utf-8')
        data = json.loads(data)
        new_username = data.get('username')
        if new_username is not None:
            # update the user's username
            request.user.username = new_username
            request.user.save()
        # get the new password from the form
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if old_password is None or new_password is None:
            return JsonResponse({'error': 'old_password is required'}, status=400)
        if not request.user.check_password(old_password):
            return JsonResponse({'error': 'invalid password'}, status=400)
        # update the user's password
        request.user.set_password(new_password)
        request.user.save()
        login(request, request.user)
        # redirect to /profile/
        return HttpResponseRedirect('/profile/')
    
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

# Handle /profile_picture/ and /profile_picture/<username>
@login_required
def profile_picture(request: ASGIRequest, username = None):
    if request.POST:
        # get the image from the form
        base64_image = request.POST.get('profile_pic')
        if base64_image is None:
            return JsonResponse({'error': 'profile_pic is required'}, status=400)
        # decode the base64 image
        image_data = base64_image.split(';base64,')[-1]
        # create an image from the base64 data
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        with BytesIO() as output:
            image.save(output, format='PNG')
            # get the user's profile
            profile = UserProfile.objects.get(user=request.user)
            # save the image
            if profile.profile_picture != 'static/beautiful_chat/default_pfp.png':
                profile.profile_picture.delete()
            profile.profile_picture.save(profile.user.username + '.png', File(output))
            profile.save()
        # return to /profile/
        return HttpResponseRedirect('/profile/')
    elif request.method == "GET" and username is not None:
        try:
            username = username.split('.')[0]
            user = User.objects.filter(username=username).first()
            profile = UserProfile.objects.get(user=user)
            if not profile:
                return JsonResponse({'error': 'user not found'}, status=404)
        except:
            return JsonResponse({'error': 'user not found'}, status=404)
        # return the image file
        return FileResponse(profile.profile_picture)
    elif request.method == 'DELETE':
        # get the user's profile
        profile = UserProfile.objects.get(user=request.user)
        # delete the profile picture
        profile.profile_picture.delete()
        # set the default profile picture
        profile.profile_picture = 'static/beautiful_chat/default_pfp.png'
        profile.save()
        # return to /profile/
        return HttpResponseRedirect('/profile/')
    
    return JsonResponse({'error': 'Not implemented'}, status=501)