from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import *
from .forms import UserSignupForm, EventForm

import json 
from django.http import JsonResponse


@login_required
def index(request):
    user = request.user
    now = timezone.now()
    
    events = Event.objects.filter(
        Q(created_by=user) | Q(invitees=user),
        date_time__gte=now
    ).distinct()

    event_data = [
        {
            "title": e.name,
            "date": e.date_time.strftime("%Y-%m-%d %H:%M"),
            "lat": e.latitude,
            "lng": e.longitude,
            "url": f"/events/{e.id}/"
        }
        for e in events if e.latitude and e.longitude
    ]

    return render(request, 'index.html', {
        "events_json": json.dumps(event_data)
    })  # Main map view

# User Related Views
class UserSignupView(CreateView):
    model = User
    form_class = UserSignupForm
    template_name = 'user_signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user) 
        return redirect('/')
    
@login_required
def user_profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    return render(request, 'profile.html', {'profile_user': profile_user})

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserSignupForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})

# Event Create Views
@login_required
def event_create(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        form.fields['invitees'].queryset = request.user.friends.all()
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            form.save_m2m()  # Save invited users
            return redirect('event_detail', event_id=event.id)
    else:
        latitude = request.GET.get('latitude', '')
        longitude = request.GET.get('longitude', '')
        form = EventForm(initial={'latitude': latitude, 'longitude': longitude})
        form.fields['invitees'].queryset = request.user.friends.all()

    return render(request, 'event_create.html', {'form': form})

@login_required
def event_list(request):
    user_created_events = Event.objects.filter(created_by=request.user)
    user_invited_events = Event.objects.filter(invitees=request.user)

    return render(request, 'event_list.html', {
        'user_created_events': user_created_events,
        'user_invited_events': user_invited_events,
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

@login_required
def event_chat(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_chat.html', {'event': event})

def user_chat_list(request):
    events = Event.objects.filter(invitees=request.user)
    return render(request, 'user_chat_list.html', {'events': events})

# Friend Views

@login_required
def friends_page(request):
    user = request.user
    friends = user.friends.all()
    incoming = user.received_requests.all()
    outgoing = user.sent_requests.all()
    others = User.objects.exclude(id=user.id).exclude(id__in=friends)

    context = {
        'friends': friends,
        'incoming_requests': incoming,
        'sent_requests': outgoing,
        'other_users': others,
    }
    return render(request, 'friends.html', context)


@require_POST
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return JsonResponse({'status': 'sent'})

def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    request.user.friends.add(friend_request.from_user)
    friend_request.from_user.friends.add(request.user)
    friend_request.delete()
    return redirect('friends_page')

def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    friend_request.delete()
    return redirect('friends_page')

@login_required
def remove_friend(request, user_id):
    user = request.user
    friend = get_object_or_404(User, id=user_id)
    user.friends.remove(friend)
    friend.friends.remove(user)
    return redirect('friends_page')
