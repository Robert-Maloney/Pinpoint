from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import UserSignupForm

@login_required
def index(request):
    return render(request, 'index.html')  # Main map view

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
        name = request.POST.get('name')
        description = request.POST.get('description')
        date_time = request.POST.get('date_time')
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))

        event = Event.objects.create(
            name=name,
            description=description,
            date_time=date_time,
            location_name="Custom Location",
            latitude=latitude,
            longitude=longitude,
            created_by=request.user
        )

        return redirect('event_detail', event_id=event.id) 

    latitude = request.GET.get('latitude', '')
    longitude = request.GET.get('longitude', '')
    context = {
        'latitude': latitude,
        'longitude': longitude,
    }
    return render(request, 'event_create.html', context)

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date_time')
    return render(request, 'event_list.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})
