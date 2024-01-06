from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from core.models import*
from django.contrib.auth.decorators import login_required
from itertools import chain
import random

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_profile=Profile.objects.get(user=request.user)
    
    user_following_list=[]
    user_following_list.append(request.user.username)
    feed=[]

    user_following=FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:#list of objects of FollowersCount
        user_following_list.append(users.user)#list of names of following

    for usernames in user_following_list:
        feed_lists=Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list=list(chain(*feed))

    #User suggestion starts
    all_users=User.objects.all()
    user_following_all=[]
        
    for user in user_following:
        user_list=User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list=[x for x in list(all_users) if (x not in list(user_following_all)) ]
    current_user=User.objects.filter(username=request.user.username)
    final_suggestions_list=[x for x in list(new_suggestions_list) if (x not in list(current_user)) ]
    
    random.shuffle(final_suggestions_list)

    username_profile=[]
    username_profile_list=[]

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile=Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile)

    suggestions_username_profile_list=list(chain(*username_profile_list))
    
    return render(request,'index.html',{
        'user_profile':user_profile,
        'posts':feed_list,
        'suggestions_username_profile_list':suggestions_username_profile_list[:4]})

def signup(request):
    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        if username=='' or email=='' or pass1=='' or pass2=='':
            messages.info(request,'Please fill all the fields')
            return redirect('signup')
        if pass1==pass2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'This e-mail is already registered')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'This username is already registered')
                return redirect('signup')
            else:
                user=User.objects.create_user(username=username, email=email, password=pass1)
                user.save()

                #Log user in and redirect to settings page
                user_login=auth.authenticate(username=username, password=pass1)
                auth.login(request,user_login)

                #Create the profile object for new user
                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model, id_user=user_model.id,)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request,'Password is not matching')
            return redirect('signup')


    else:
        return render(request,'signup.html')
    
def signin(request):

    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Credential Invalid')
            return redirect('/signin')
    else:
        return render(request,'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def settings(request):
    user_profile=Profile.objects.get(user=request.user)

    if request.method=='POST':

        if request.FILES.get('profile-pic')==None:
            image=user_profile.profileimg
            bio=request.POST['bio']
            location=request.POST['location']

            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()
        if request.FILES.get('profile-pic') !=None:
            image=request.FILES.get('profile-pic')
            bio=request.POST['bio']
            location=request.POST['location']

            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()
            return redirect('settings')
        return redirect('index')
        # return render(request,'index.html',{'user_profile':user_profile})
    return render(request,'settings.html',{'user_profile':user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method=="POST":
        user_profile=Profile.objects.get(user=request.user)
        user=request.user.username
        image=request.FILES.get('image_upload')
        caption=request.POST.get('caption')
        icon=user_profile.profileimg
        if image==None:
            return redirect("/")
        
        new_post=Post.objects.create(
            user=user,
            image=image,
            caption=caption,
            icon=icon,
        )
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')
    
@login_required(login_url='sign-in')
def like_post(request):
    username=request.user.username
    post_id=request.GET.get('post_id')
    page=request.GET.get('page')
    post=Post.objects.get(id=post_id)
    
    like_filter=LikePost.objects.filter(username=username,post_id=post_id).first()
    
    if like_filter==None:
        new_like=LikePost.objects.create(
            username=username,
            post_id=post_id
        )
        new_like.save()
        post.no_of_likes+=1
        post.save()
        print(page)
        if page==None:
            return redirect('/#'+post_id)
        else:
            return redirect('/profile/'+page+'#'+post_id)
        
    else:
        like_filter.delete()
        post.no_of_likes-=1
        post.save()
        print(page)
        if page==None:
            return redirect('/#'+post_id)
        else:
            return redirect('/profile/'+page+'#'+post_id)

@login_required(login_url='sign-in')
def profile(request,pk):
    Cuser_profile=Profile.objects.get(user=request.user)
    user_object=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user_object)
    user_post=Post.objects.filter(user=pk)
    user_post_length=len(user_post)

    follower=request.user.username
    user=pk
    if FollowersCount.objects.filter(follower=follower,user=user).first():
        button_text='Unfollow'
    else:
        button_text='Follow'

    user_followers=len(FollowersCount.objects.filter(user=pk))
    user_followings=len(FollowersCount.objects.filter(follower=pk))

    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'user_post':user_post,
        'user_post_length':user_post_length,
        'Cuser_profile':Cuser_profile,
        'button_text':button_text,
        'user_followers':user_followers,
        'user_followings':user_followings,
    }
    return render(request,'profile.html',context)
    
@login_required(login_url='sign-in')
def follow(request):
    if request.method=='POST':
        follower=request.POST['follower']
        user=request.POST['user']

        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower=FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower=FollowersCount.objects.create(follower=follower,user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')
    
@login_required(login_url='sign-in')
def search(request):
    if request.method=="POST":
        username=request.POST['username']
        username_object=User.objects.filter(username__icontains=username)

        username_profile=[]
        username_profile_list=[]
        
        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists=Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list=list(chain(*username_profile_list))
    return render(request,'search.html',{'username_profile_list':username_profile_list})