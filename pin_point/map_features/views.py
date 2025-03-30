from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import *
from .forms import UserSignupForm, EventForm
import json


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