"""shiba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

import game.views

urlpatterns = [
    path("NewImage/", game.views.new_image),
    path("QuestCount/", game.views.quest_count),
    path("UserImage/", game.views.user_image),
    path("AddLocationLogJSON/", game.views.add_location_log),
    path('QuestList/', game.views.quest_list),
    path('AddFriendJSON/', game.views.add_friend),
    path('FriendList/', game.views.friend_list),
    path('PetLevel/', game.views.pet_level),
    path('RegistrationJSON/', game.views.registration),
    path('LoginJSON/', game.views.login),
    path('admin/', admin.site.urls),
]
