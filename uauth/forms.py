from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

	class Meta(UserCreationForm):
		model = CustomUser
		fields = ("username", "email", "password1", "password2",)

class CustomUserChangeForm(UserChangeForm):

	class Meta(UserChangeForm):
		model = CustomUser
		fields = UserChangeForm.Meta.fields