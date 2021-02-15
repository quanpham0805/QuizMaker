from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView


# Create your views here.

class LoginPageView(TemplateView):
	template_name = "uauth/login.html"

class RegisterPageView(TemplateView):
	template_name = "uauth/register.html"
