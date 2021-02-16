from django.shortcuts import render
from django.views.generic import TemplateView

class QuizListView(TemplateView):
	template_name = "quiz_list/quizlist.html"

class AddQuizView(TemplateView):
	template_name = "quiz_list/addquiz.html"


# Create your views here.
