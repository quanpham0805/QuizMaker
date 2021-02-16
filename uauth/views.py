from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm


# Create your views here.

class LoginPageView(LoginView):
	template_name = "uauth/login.html"
	redirect_authenticated_user = True


class RegisterPageView(CreateView):
	template_name = "uauth/register.html"
	form_class = CustomUserCreationForm
	success_url = reverse_lazy('homepage')
