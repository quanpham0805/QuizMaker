# pages/urls.py
from django.urls import path
from .views import QuizListView, AddQuizView, CustomizeWordView, deleteWord, doQuiz, finishQuiz

urlpatterns = [
	path('quizlist/', QuizListView.as_view(), name='quizlist'),
	path('addquiz/', AddQuizView.as_view(), name='addquiz'),
	path('customizeword/', CustomizeWordView.as_view(), name='customize_word'),
	path('deleteword/', deleteWord, name='delete_word'),
	path('doquiz/', doQuiz, name='do_quiz'),
	path('finish/', finishQuiz, name='finish'),
]