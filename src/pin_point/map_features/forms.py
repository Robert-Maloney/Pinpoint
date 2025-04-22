from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.timezone import now
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
        fields = ['name', 'description', 'start_time', 'end_time', 'location_name', 'latitude', 'longitude', 'is_public', 'invitees', 'tags']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'tags': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        if start and start < now():
            raise forms.ValidationError("Start time must be in the future.")
        
        if end and end < now():
            raise forms.ValidationError("End time must be in the future.")

        if start and end and end <= start:
            raise forms.ValidationError("End time must be after start time.")