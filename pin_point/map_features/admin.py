from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Pin)
admin.site.register(Photo)
admin.site.register(Event)
admin.site.register(Message)