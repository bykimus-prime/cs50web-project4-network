from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like


def index(request):
   allPosts = Post.objects.all().order_by("id").reverse() # show posts by most recent

   # pagination
   paginator = Paginator(allPosts, 10) # input is allPosts, shows 10 posts at a time
   pageNumber = request.GET.get('page') # page number to show on index
   postsOfPage = paginator.get_page(pageNumber) # display posts by pages

   # get all likes
   allLikes = Like.objects.all()
   # get all posts that user liked
   whoYouLiked = []
   # if user is not signed in, return empty list
   try:
      for like in allLikes:
         if like.user.id == request.user.id:
            whoYouLiked.append(like.post.id)
   except:
      whoYouLiked = []

   return render(request, "network/index.html", {
      "allPosts": allPosts,
      "postsOfPage": postsOfPage,
      "whoYouLiked": whoYouLiked
   })

def remove_like(request, post_id):
   post = Post.objects.get(pk=post_id)
   user = User.objects.get(pk=request.user.id)
   like = Like.objects.filter(user=user, post=post)
   like.delete()
   return JsonResponse({"message": "Thumbs down"})

def add_like(request, post_id):
   post = Post.objects.get(pk=post_id)
   user = User.objects.get(pk=request.user.id)
   newLike = Like(user=user, post=post)
   newLike.save()
   return JsonResponse({"message": "Thumbs up"})

def edit(request, post_id):
   if request.method == "POST": # check if we're receiving a post method
      data = json.loads(request.body) # get data from javascript
      edit_post = Post.objects.get(pk=post_id) # get data from particular post
      edit_post.content = data["content"] # change content of this post
      edit_post.save()
      return JsonResponse({"message": "Change successful", "data": data["content"]}) # return a json response to our frontend again

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

   follower = Follow.objects.filter(user=user)
   followed = Follow.objects.filter(user_followed=user)

   try:
      checkFollow = followed.filter(user=User.objects.get(pk=request.user.id))
      if len(checkFollow) != 0:
         isFollowing = True
      else:
         isFollowing = False
   except:
      isFollowing = False

   # pagination
   paginator = Paginator(allPosts, 10)
   pageNumber = request.GET.get('page')
   postsOfPage = paginator.get_page(pageNumber)

   return render(request, "network/profile.html", {
      "allPosts": allPosts,
      "postsOfPage": postsOfPage,
      "username": user.username,
      "follower": follower,
      "followed": followed,
      "isFollowing": isFollowing,
      "user_profile": user
   })

def following(request):
   currentUser = User.objects.get(pk=request.user.id) # gets all data about that particular user
   followingPeople = Follow.objects.filter(user=currentUser) # get all people that this user follows
   allPosts = Post.objects.all().order_by('id').reverse() # get all posts available
   
   followingPosts = [] # display posts only for people user is following

   for post in allPosts:
      for person in followingPeople:
         if person.user_followed == post.user:
            followingPosts.append(post)

   # pagination
   # input is allPosts, shows 10 posts at a time
   paginator = Paginator(followingPosts, 10)
   pageNumber = request.GET.get('page')  # page number to show on index
   postsOfPage = paginator.get_page(pageNumber)  # display posts by pages

   return render(request, "network/following.html", {
      "postsOfPage": postsOfPage
   })

def follow(request):
   userFollow = request.POST['userFollow']
   currentUser = User.objects.get(pk=request.user.id)
   userFollowData = User.objects.get(username=userFollow)
   f = Follow(user=currentUser, user_followed=userFollowData)
   f.save()
   user_id = userFollowData.id
   return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def unfollow(request):
   userFollow = request.POST['userFollow']
   currentUser = User.objects.get(pk=request.user.id)
   userFollowData = User.objects.get(username=userFollow)
   f = Follow.objects.get(user=currentUser, user_followed=userFollowData)
   f.delete()
   user_id = userFollowData.id
   return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

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
