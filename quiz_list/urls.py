# pages/urls.py
from django.urls import path
from .views import QuizListView, AddQuizView

urlpatterns = [
	path('quizlist', QuizListView.as_view(), name='quizlist'),
	path('addquiz', AddQuizView.as_view(), name='addquiz'),
]