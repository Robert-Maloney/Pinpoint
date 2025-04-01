from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import UserSignupView, user_profile, edit_profile, index
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('create-event/', views.event_create, name='create_event'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('ws/chat/<int:event_id>/', views.event_chat, name='event_chat'),
    path('events/chats/', views.user_chat_list, name='user_chat_list'),
    path('register/', UserSignupView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.user_profile, name='my_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='friend_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('friends/', views.friends_page, name='friends_page'),
    path('friends/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
]
