import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import *

def index(request):
    return render(request, 'index.html')  # Map for selecting a location

def event_create(request):
    latitude = request.GET.get('latitude', None)
    longitude = request.GET.get('longitude', None)
    context = {
        'latitude': latitude,
        'longitude': longitude,
    }
    return render(request, 'event_create.html', context)


@login_required
def event_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        date_time = request.POST.get('date_time')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Create and save the event
        Event.objects.create(
            name=name,
            description=description,
            date_time=date_time,
            location_name="Custom Location",
            latitude=latitude,
            longitude=longitude,
            created_by=request.user
        )
        return JsonResponse({"message": "Event created successfully!"})
    
    latitude = request.GET.get('latitude', None)
    longitude = request.GET.get('longitude', None)
    context = {
        'latitude': latitude,
        'longitude': longitude,
    }
    return render(request, 'event_create.html', context)

