from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post


def index(request):
   allPosts = Post.objects.all().order_by("id").reverse() # show posts by most recent

   # pagination
   paginator = Paginator(allPosts, 10) # input is allPosts, shows 10 posts at a time
   pageNumber = request.GET.get('page') # page number to show on index
   postsOfPage = paginator.get_page(pageNumber) # display posts by pages

   return render(request, "network/index.html", {
      "allPosts": allPosts,
      "postsOfPage": postsOfPage
   })

def new_post(request):
   if request.method == "POST":
      content = request.POST['content']
      user = User.objects.get(pk=request.user.id)
      post = Post(content=content, user=user)
      post.save()
      return HttpResponseRedirect(reverse(index))

def profile(request, user_id):
   user = User.objects.get(pk=user_id)
   allPosts = Post.objects.filter(user=user).order_by("id").reverse()  # show only user's posts

   # pagination
   paginator = Paginator(allPosts, 10)
   pageNumber = request.GET.get('page')
   postsOfPage = paginator.get_page(pageNumber)

   return render(request, "network/profile.html", {
      "allPosts": allPosts,
      "postsOfPage": postsOfPage,
      "username": user.username
   })

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
