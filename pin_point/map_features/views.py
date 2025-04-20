from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.timezone import now, localtime
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import *
from .forms import UserSignupForm, EventForm

import json 
from django.http import JsonResponse


@login_required
def index(request):
    user = request.user
    
    events = Event.objects.filter(
    Q(is_public=True) | Q(created_by=user) | Q(invitees=user),
    end_time__gte=now()
    ).distinct()

    event_data = [
        {
            "title": e.name,
            "lat": e.latitude,
            "lng": e.longitude,
            "url": f"/events/{e.id}/",
            "ongoing": e.start_time <= now() <= e.end_time,
            "date": localtime(e.start_time).strftime("%a, %b %d %Y %H:%M"),
            "end_time": e.end_time.strftime("%Y-%m-%d %H:%M"),
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
    return render(request, 'profile.html', {'profile_user': user})

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
    favourites = FavouriteLocation.objects.filter(user=request.user)

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
        place_name = request.GET.get('name', '')
        form = EventForm(initial={'latitude': latitude, 'longitude': longitude, 'location_name': place_name, 'name': place_name})
        form.fields['invitees'].queryset = request.user.friends.all()

    return render(request, 'event_create.html', {'form': form, 'favourites': favourites})

@login_required
def event_list(request):
    now_time = timezone.now()

    user_events = Event.objects.filter(
        Q(created_by=request.user) | Q(invitees=request.user)
    ).distinct()

    upcoming_events = user_events.filter(end_time__gte=now_time)
    past_events = user_events.filter(end_time__lt=now_time)

    return render(request, 'event_list.html', {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'now': now_time,
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_rsvp = RSVP.objects.filter(user=request.user, event=event).first()

    all_rsvps = RSVP.objects.filter(event=event)

    event_has_ended = event.end_time < now()
    memories = event.memories.all()

    if request.method == "POST" and event_has_ended and request.FILES.get("image"):
        EventPhoto.objects.create(
            event=event,
            user=request.user,
            image=request.FILES["image"]
        )
        return redirect('event_detail', event_id=event.id)

    return render(request, 'event_detail.html', {'event': event, 'user_rsvp': user_rsvp, 'all_rsvps': all_rsvps, "event_has_ended": event_has_ended, "memories": memories})

@login_required
def event_chat(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_chat.html', {'event': event})

def user_chat_list(request):
    events = Event.objects.filter(invitees=request.user)
    return render(request, 'user_chat_list.html', {'events': events})

@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return redirect('event_detail', event_id=event.id)

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user != event.created_by:
        return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')

    return render(request, 'event_confirm_delete.html', {'event': event })


# Friend Views

@login_required
def friends_page(request):
    user = request.user
    friends = user.friends.all()
    incoming = user.received_requests.all()
    outgoing = user.sent_requests.all()
    sent_users = outgoing.values_list('to_user__id', flat=True)
    others = User.objects.exclude(id=user.id).exclude(id__in=friends).exclude(id__in=sent_users)

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

def settings_view(request):
   if request.method == 'POST':
      user = request.user
      user.is_marketing_user = 'is_marketing_user' in request.POST
      user.save()
      return redirect('settings')
   
   return render(request, 'settings.html', {'user': request.user})

@login_required
def marketing_dashboard(request):
   user = request.user
   if not user.is_marketing_user:
      return redirect("home")

   events = Event.objects.filter(created_by=user)
   rsvp_stats = {e.id: RSVP.objects.filter(event=e).count() for e in events}
   chat_activity = {e.id: Message.objects.filter(event=e).count() for e in events}

   context = {
      "events": events,
      "rsvp_stats": rsvp_stats,
      "chat_activity": chat_activity,
   }
   return render(request, "marketing_dashboard.html", context)