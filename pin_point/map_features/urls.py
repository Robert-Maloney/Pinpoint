from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import UserSignupView, user_profile, edit_profile, index
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('create-event/', views.event_create, name='create_event'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('ws/chat/<int:event_id>/', views.chat_view, name='chat'),
    path('register/', UserSignupView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', user_profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]
