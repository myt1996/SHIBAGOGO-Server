import base64
import json
import os
from datetime import datetime, timedelta

import numpy as np
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pytz import timezone

from game.models import APPUser, Friend, LocationLog, Pet, Place, Quest
from shiba_tools.place_api import find_place
from shiba_tools.suisen import recommend_system


def index(request):
    return HttpResponse("Hello, world. You're at the pet index. Only for test.")

# RegistrationJSON
@csrf_exempt
def registration(request):
    keys = ["userMailAddress", "userPassword", "userInitialInfo1",
            "userInitialInfo2", "userInitialInfo3", "userInitialInfo4", "userImage"]
    dict = json_from_request(request, "POST", keys)
    if dict:
        username = dict.get("userMailAddress")
        if User.objects.filter(username=username).exists():
            return HttpResponse("Username has been used.")

        password = dict.get("userPassword")
        info_raw = (dict.get("userInitialInfo1"), dict.get("userInitialInfo2"), dict.get(
            "userInitialInfo3"), dict.get("userInitialInfo4"))
        image_raw = dict.get("userImage")

        # process info
        info = registration_info_process(info_raw)
        # process image
        image = registration_image_process(image_raw, username)
        # generate token
        token = token_generate(username)
        user = User.objects.create_user(username, username, password)
        app_user = APPUser(user=user, info=info, image=image, token=token)
        app_user.save()
        # generate pet
        pet = Pet(user=user, name="Pet", level=1, status="Normal")
        pet.save()

        return HttpResponse(token)
    else:
        return HttpResponse("JSON POST error.", status=400)


def registration_info_process(info):
    return int(info[0]*1000+info[1]*100+info[2]*10+info[3])

def registration_image_process(image, username):
    image_data = base64.b64decode(image)
    with open(username+".png", "wb") as f:
        f.write(image_data)
    return username

def token_generate(username):
    return username

# LoginJSON 
@csrf_exempt
def login(request):
    keys = ["userMailAddress", "userPassword"]
    dict = json_from_request(request, "POST", keys)
    if dict:
        username = dict.get("userMailAddress")
        password = dict.get("userPassword")
        user = authenticate(username=username, password=password)
        if user is not None:
            token = token_generate(username)
            return HttpResponse(token)
        else:
            return HttpResponse("Wrong username or password.", status=401)
    else:
        return HttpResponse("Should post username and password when login.", status=400)


'''
    args:
        request, should be a json request
        method, method allowed, POST or GET
        keys, request json should contains thest keys
    return:
        None if request dont meet necessary
        dict otherwise
'''
def json_from_request(request, method='POST', keys=[]):
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

# PetLevel  
@csrf_exempt
def pet_level(request):
    try:
        token = request.body.decode("utf-8")
        app_user = APPUser.objects.get(token=token)
        user = app_user.user
    except:
        return HttpResponse("Wrong token", status=401)
    level = Pet.objects.get(user=user).level
    return HttpResponse(str(level))

# FriendList  
@csrf_exempt
def friend_list(request):
    try:
        token = request.body.decode("utf-8")
        app_user = APPUser.objects.get(token=token)
        user = app_user.user
    except:
        return HttpResponse("Wrong token", status=401)
    friends_query = Friend.objects.filter(user=user)

    friends = []
    for f in friends_query:
        end_user = f.friend
        end_user_pet_level = Pet.objects.get(user=end_user).level
        end_username = end_user.username
        end_user_image = APPUser.objects.get(user=end_user).image
        friends.append([end_username, end_user_pet_level, end_user_image])
    friends.sort(key=lambda tup: tup[1], reverse=True)

    friend_dicts = []
    ranking = 1
    for f in friends:
        dict = {}
        dict["ranking"] = ranking
        dict["name"] = f[0]
        dict["level"] = f[1]
        dict["imagepath"] = f[2]
        friend_dicts.append(dict)
        ranking += 1
    json_str = json.dumps(friend_dicts)

    return HttpResponse(json_str)

# AddFriend 
@csrf_exempt
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
            user = app_user.user
            end_user = User.objects.get(username=end_username)
        except:
            return HttpResponse("Wrong token", status=401)
        f = Friend(user=user, friend=end_user)
        f.save()
        return HttpResponse("Success")
    else:
        return HttpResponse("Wrong request", status=400)


QUEST_STATUS = {0: "Completed", 1: "On going", 2: "Out of data"}
QUEST_DATA_FORMAT = 'End at %Y-%m-%d %H:%M:%S'


def check_quest_status(pk, out_date, cur_date):
    if out_date < cur_date:
        status = 2
    else:
        status = 1
    Quest.objects.filter(pk=pk).update(status=status)

def check_quest_completed(user):
    raise NotImplementedError

def set_new_quest(user):
    data_recoder = np.load(os.path.join( os.getcwd(), "data_recoder.npy"))
    time_recoder = np.load(os.path.join( os.getcwd(), "time_recoder.npy"))
    rs = recommend_system(time_recoder, data_recoder)
    place_index = rs.suggest_place #.recommend()

    zahyou_index_ls = [[34.992662, 135.952072], [34.979477, 135.964416], [35.003617, 135.951241],
                       [34.995388, 135.952798], [34.981981, 135.962519]]
    x, y = zahyou_index_ls[int(place_index)]
    place = Place.objects.get(x=x, y=y)
    name = "Go to {}".format(place.name)
    quest = Quest(user=user, name=name, place=place, start=datetime.now(), end=datetime.now()+timedelta(days=1), status=1, info=name)
    quest.save()

# QuestList  
@csrf_exempt
def quest_list(request):
    try:
        token = request.body.decode("utf-8")
        app_user = APPUser.objects.get(token=token)
        user = app_user.user
    except:
        return HttpResponse("Wrong token", status=401)

    quests_query = Quest.objects.filter(user=user)

    quests_dicts = []
    for q in quests_query:
        dict = {}
        dict["mission"] = q.name
        dict["date"] = (datetime.now() + timedelta(days=1)
                        ).strftime(QUEST_DATA_FORMAT)
        dict["state"] = QUEST_STATUS[q.status]
        dict["content"] = q.info
        dict["latitude"] = q.place.x
        dict["longtitude"] = q.place.y
        quests_dicts.append(dict)
    json_str = json.dumps(quests_dicts)

    return HttpResponse(json_str)

# QuestCount  
@csrf_exempt
def quest_count(request):
    try:
        token = request.body.decode("utf-8")
        app_user = APPUser.objects.get(token=token)
        user = app_user.user
    except:
        return HttpResponse("Wrong token", status=401)

    quests_query = Quest.objects.filter(user=user)
    count = 0
    for q in quests_query:
        if q.status == 1:
            count += 1

    return HttpResponse(str(count))

# AddLocationLogJSON 
@csrf_exempt
def add_location_log(request):
    keys = ["token", "timeLocationinfo"]
    dict = json_from_request(request, 'POST', keys)
    if dict:
        try:
            token = dict["token"]
            time_locations = dict["timeLocationinfo"]
        except:
            return HttpResponse("Wrong request", status=400)
        try:
            app_user = APPUser.objects.get(token=token)
            user = app_user.user
        except:
            return HttpResponse("Wrong token", status=401)

        # if time_locations == "":
        #     with open(os.path.join( os.getcwd(), "location_log.json"), "r") as f:
        #         json_str = f.read()
        #     time_locations = json.loads(json_str)

        JST = timezone('Asia/Tokyo')

        for time_location in time_locations:
            time = datetime.fromtimestamp(time_location["date"], JST)
            x = time_location["lat"]
            y = time_location["lng"]

            try:
                place_query = Place.objects.filter(x=x, y=y)
                place = place_query[0]
            except:
                place = place
                # Save google map api cost
                # place_info = find_place(x, y)
                # place = Place(
                #     x=x, y=y, name=place_info["name"], type=0, info=place_info)
                # place.save()

            log = LocationLog(user=user, time=time, place=place)
            log.save()

        set_new_quest(user)
        return HttpResponse("Success")
    else:
        return HttpResponse("Wrong request", status=400)

# UserImage  
@csrf_exempt
def user_image(request):
    try:
        username = request.body.decode("utf-8")
        filename = os.path.join( os.getcwd(), "data", username+".png" )
        with open(filename, "rb") as f:
            data = f.read()
        return HttpResponse(data)
    except:
        return HttpResponse("Wrong username", status=401)
