import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from itertools import chain

from .models import User, Post

class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content']


def index(request, type="none"):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = NewPostForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.poster = request.user
                f.save()
                form.save_m2m()
                return HttpResponseRedirect(reverse("index"))
            else:
                return HttpResponse("Error saving post")
        else:
            HttpResponse("Unauthenticated user")
    print('index view')
    return render(request, "network/index.html", {
        "form": NewPostForm(),
        "type": type
    })

def posts(request, type):
    if type == "all":
        posts = Post.objects.all()
    elif type=="following":
        posts = Post.objects.none()
        person = User.objects.get(username = request.user.username)
        following = person.following.all()
        for user in following:
            userPosts = Post.objects.filter(poster=user)
            posts = posts | userPosts
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    posts = posts.order_by("-timestamp").all()
    return JsonResponse([post.serialize(request.user) for post in posts], safe=False)

@csrf_exempt
def post(request, id):
    if request.method == "PUT":
        post = Post.objects.get(id = id);
        liked = True
        if (post.likes.contains(request.user)):
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
        post.save()
        response = JsonResponse({"likes":post.likes.count()}, status=204)
        print(response.content)
        return response

@csrf_exempt
@login_required
def profile(request, profile):
    try:
        person = User.objects.get(username = profile)
    except User.DoesNotExist:
        return JsonResponse({"error": "Username not found"}, status=404)

    if request.method == "GET":
        followInfo = person.followInfo()
        if (person.followers.contains(request.user)):
            following = True
        else:
            following = False
        return render(request, "network/profile.html", {
        "followInfo" : followInfo,
        "following": following,
        "proname":followInfo['user']
    })

    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("follow") is not None:
            if (data["follow"]):
                person.followers.add(request.user)
            else:
                person.followers.remove(request.user)
            person.save()
        return HttpResponse(status=204)
        

def justChecking(request):
    return render(request, "network/justChecking.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
