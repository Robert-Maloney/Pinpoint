from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


# Create your models here.

from django.db import models

class Pin(models.Model):
   title = models.CharField(max_length=255, blank=True, null=True)  # Optional title for the pin
   latitude = models.FloatField()
   longitude = models.FloatField()
   event_time = models.DateTimeField(null=True, blank=True)  # Allow null and blank values
   created_at = models.DateTimeField(auto_now_add=True, null=True)

   def __str__(self):
      return f"Pin at ({self.latitude}, {self.longitude})"

class Photo(models.Model):
   image = models.ImageField(upload_to='photos/')
   pin = models.ForeignKey(Pin, on_delete=models.CASCADE, related_name='photos')
   public = models.BooleanField(default=True)


class Event(models.Model):
   name = models.CharField(max_length=255)
   description = models.TextField(blank=True, null=True)
   date_time = models.DateTimeField()
   location_name = models.CharField(max_length=255)  # e.g., DCU Nubar
   latitude = models.FloatField()
   longitude = models.FloatField()
   private = models.BooleanField(default=False)
   created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
   invitees = models.ManyToManyField(User, related_name="event_invitations", blank=True)

   def __str__(self):
      return self.name
