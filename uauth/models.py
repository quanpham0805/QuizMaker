from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
	number_of_quizzes = models.PositiveIntegerField(blank=True, default=0)
	attempts=models.PositiveIntegerField(blank=True, default=0)