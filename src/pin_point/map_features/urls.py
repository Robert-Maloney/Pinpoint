from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from .views import UserSignupView, user_profile, edit_profile, index, LogoutViewGET
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('create-event/', views.event_create, name='create_event'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('ws/chat/<int:event_id>/', views.event_chat, name='event_chat'),
    path('events/chats/', views.user_chat_list, name='user_chat_list'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    path('register/', UserSignupView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutViewGET.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('profile/', views.user_profile, name='my_profile'),
    path('profile/<int:user_id>/', views.view_profile, name='friend_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path("settings/", views.settings_view, name="settings"),

    path('friends/', views.friends_page, name='friends_page'),
    path('friends/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friends/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friends/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),

    path("marketing/dashboard/", views.marketing_dashboard, name="marketing_dashboard"),
    path('public-create-event/', views.public_event_create, name='public_create_event'),
]
