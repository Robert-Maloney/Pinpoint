from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Event
from django.db import transaction

class UserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'profile_photo', 'password1', 'password2']

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.phone = self.cleaned_data.get('phone')
        user.profile_photo = self.cleaned_data.get('profile_photo')
        user.is_admin = False
        user.save()
        return user

class EventForm(forms.ModelForm):
    invitees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Event
        fields = ['name', 'description', 'date_time', 'location_name', 'latitude', 'longitude', 'private', 'invitees']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'latitude': forms.TextInput(attrs={'readonly': True}),
            'longitude': forms.TextInput(attrs={'readonly': True}),
        }