# For json reuqest
import json

import qrcode
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from game.models import APPUser, Pet, Friend, Quest, Place

# Create your views here.

# / for test
def index(request):
    # users = User.objects.all()
    # for user in users:
    #     user.delete()
    # # user create test
    # User.objects.create_user(username="myt", email="mytemail", password="123456")
    # # user get test
    # APPUser.objects.create(user=myt_user)
    # myt_appuser = myt_user.app_user
    # # pet create test
    # Pet.objects.create(user=myt_appuser, name="mytpet", level=100, status="Normal")
    # # pet get test
    # myt_pet = Pet.objects.get(user=myt_appuser)
    # # delete test
    # myt_appuser.delete()
    return HttpResponse("Hello, world. You're at the pet index. Only for test.")

# Old version
# def registration(request):
#     form = UserForm(request.POST, request.FILES)
#     if form.is_valid():
#         username = request.POST["username"]
#         password = request.POST["password"]

#         if User.objects.filter(username=username).exists():
#             return HttpResponse("Username has been used.")
    
#         # Here wo dont check the password because we hope client will do this
#         user = User.objects.create_user(username, username, password)
#         # Create QRCode for this user
#         # qr_str = "shiba://user/{}".format(username)
#         # qr_image = qrcode.make(qr_str)
#         # qr_save_path = "Data/QR/{}.png".format(username)
#         # qr_image.save(qr_save_path)
#         # Also create app_user with created user and QRCode
#         app_user = APPUser(user=user)
#         app_user.save()
#         return HttpResponse("Success.")
#     else:
#         return HttpResponse("Should post username and password for registration.", status=400)

# Registration only POST, new version cannot past test now
def registration(request):
    keys = ["userMailAddress", "userPassword", "userInitialInfo", "userImage"]
    dict = json_from_request(request, "POST", keys)
    if dict:
        username = dict.get("userMailAddress")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username has been used.")

        password = dict.get("userPassword")
        info_raw = dict.get("userInitialInfo")
        image_raw = dict.get("userImage")
        user = User.objects.create_user(username, username, password)
        # TODO create app_user

        # process info
        info = registration_info_process(info_raw)
        # process image
        image = registration_image_process(image_raw)
        # generate token
        token = token_generate(username)
        app_user = APPUser(user=user, info=info, image=image, token=token)
        app_user.save()

        return HttpResponse(token)
    else:
        return HttpResponse("JSON POST error.", status=400)

def registration_info_process(info):
    raise NotImplementedError
def registration_image_process(image):
    raise NotImplementedError
def token_generate(username):
    return username

# Login only POST
def login(request):
    form = UserForm(request.POST, request.FILES)
    if form.is_valid():
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            token = token_generate(username)
            return HttpResponse(token)
        else:
            return HttpResponse("Wrong username or password.", status=401)
    else:
        return HttpResponse("Should post username and password when login.", status=400)

def json_post(request):
    dict = json_from_request(request)
    if dict:
        method_str = dict["method"]
        if method_str in globals():
            method = globals()[method_str]
            return_value = method(dict)
            if return_value == True:
                return HttpResponse("Success.")
            else:
                return HttpResponse("Failed.")
        else:
            return HttpResponse("JSON POST error.", status=400)
    else:
        return HttpResponse("JSON POST error.", status=400)

def test_bool_function(dict):
    if "test_bool" in dict.keys() and isinstance(dict["test_bool"], bool):
        return dict["test_bool"]
    else:
        return False

class UserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
class TokenForm(forms.Form):
    token = forms.CharField()

'''
    args:
        request, should be a json request
        method, method allowed, POST or GET
        keys, request json should contains thest keys
    return:
        None if request dont meet necessary
        dict otherwise
'''
def json_from_request(request, method='POST', keys = []):
    if request.method == method:
        try:
            dict = json.loads(request.body)
            # if "method" in dict.keys() and dict["method"] is not None:
            #     return dict
            # else:
            #     #print("JSON request must contain a 'method' key")
            #     return None
            for key in keys:
                if key not in dict.keys():
                    return None
            return dict
        except:
            #print("{} is not a JSON request".format(request.body.decode("utf-8")))
            return None
    else:
        #print("Request method is {} but POST expected".format(request.method))
        return None

# PetLevel only GET
def pet_level(request):
    #if request.user.is_authenticated and request.method == 'GET':
    form = TokenForm(request.GET, request.FILES)
    if form.is_valid():
        token = form["token"]
        app_user = APPUser.objects.get(token=token)
        user = app_user.user
        level = Pet.objects.get(user=user).level
        return HttpResponse(str(level))
    else:
        return HttpResponse("Wrong request", status=400)

# FriendList only GET
def friend_list(request):
    # if request.user.is_authenticated and 
    if request.method == 'GET':
        try:
            token = request.GET["token"]
        except:
            return HttpResponse("Wrong request", status=400)
        try:
            app_user = APPUser.objects.get(token=token)
            user = User.objects.get(APPUser=app_user)
        except:
            return HttpResponse("Wrong token", status=401)
        friends_query = Friend.objects.filter(user=user)

        friends = []
        for f in friends_query:
            end_user = f.friend
            end_user_pet_level  = Pet.objects.get(user=end_user).level
            end_username = f.username
            end_user_image = APPUser.objects.get(user=end_user).end_user_image
            friends.append([end_username, end_user_pet_level, end_user_image])
        friends.sort(key=lambda tup: tup[1], reverse=True)
        
        friend_dicts = []
        for f in friends:
            dict = {}
            dict["name"] = f[0]
            dict["level"] = f[1]
            dict["imagepath"] = f[2]
            friend_dicts.append(dict)
        
        return JsonResponse(friend_dicts)
    else:
        return HttpResponse("Wrong request", status=400)

# AddFriend only POST
def add_friend(request):
    keys = ["token", "friendname"]
    dict = json_from_request(request, 'POST', keys)
    if dict:
        try:
            token = dict["token"]
            end_username = dict["friendname"]
        except:
            return HttpResponse("Wrong request", status=400)
        try:
            app_user = APPUser.objects.get(token=token)
            user = User.objects.get(APPUser=app_user)
            end_user = User.objects.get(username=end_username)
        except:
            return HttpResponse("Wrong token", status=401)
        f = Friend(user=user, friend=end_user)
        f.save()
        return HttpResponse("Success")
    else:
        return HttpResponse("Wrong request", status=400)

# QuestList only GET
def quest_list(request):
    # if request.user.is_authenticated and 
    if request.method == 'GET':
        try:
            token = request.GET["token"]
        except:
            return HttpResponse("Wrong request", status=400)
        try:
            app_user = APPUser.objects.get(token=token)
            user = User.objects.get(APPUser=app_user)
        except:
            return HttpResponse("Wrong token", status=401)
        quests_query = Quest.objects.filter(user=user)

        quests_dicts = []
        for q in quests_query:
            dict = {}
            dict["misson"] = q.info
            dict["date"] = q.end
            dict["state"] = q.status
            quests_dicts.append(dict)
        
        return JsonResponse(quests_dicts)
    else:
        return HttpResponse("Wrong request", status=400)