from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings

from datetime import datetime

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
   email = models.EmailField(unique=True)
   phone = models.CharField(max_length=15, blank=True, null=True)
   profile_photo = models.ImageField(
      upload_to='profile_photos/', 
      blank=True, 
      null=True
   )
   friends = models.ManyToManyField("self", blank=True, symmetrical=True)

   def get_profile_photo(self):
      if self.profile_photo:
        return self.profile_photo.url
      return "/static/icons/default_profile.jpg"  
   
   def __str__(self):
      return self.username

class FriendRequest(models.Model):
   from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
   to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
   timestamp = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return f"{self.from_user} → {self.to_user}"

class Pin(models.Model):
   title = models.CharField(max_length=255, blank=True, null=True)
   latitude = models.FloatField()
   longitude = models.FloatField()
   event_time = models.DateTimeField(null=True, blank=True)
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
   start_time = models.DateTimeField()
   end_time = models.DateTimeField()
   location_name = models.CharField(max_length=255)
   latitude = models.FloatField()
   longitude = models.FloatField()
   is_public = models.BooleanField(default=True)
   created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events")
   invitees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="event_invitations", blank=True)
   
   def __str__(self):
      return self.name

class Message(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   message = models.TextField()
   timestamp = models.DateTimeField(auto_now_add=True)

   class Meta:
      ordering = ['timestamp']
     
   def __str__(self):
      return f"{self.user} at {self.timestamp}: {self.message}"
   
class FavouriteLocation(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   name = models.CharField(max_length=255)
   latitude = models.FloatField()
   longitude = models.FloatField()

   def __str__(self):
      return f"{self.name} ({self.latitude}, {self.longitude})"
   
class RSVP(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   event = models.ForeignKey(Event, on_delete=models.CASCADE)
   status = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')])

