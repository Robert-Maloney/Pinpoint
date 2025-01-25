from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create-event/', views.event_create, name='create_event'),
]
