from django import forms
from .models import QuizList, Word
from django.forms import ModelForm

class QuizListModelForm(ModelForm):

	class Meta:
		model = QuizList
		fields = ['quiz_name', 'time_limit', 'quiz_language']

class QuizListDisplayForm(QuizListModelForm):
	word_list = forms.CharField(widget=forms.Textarea)

class WordForm(ModelForm):

	class Meta:
		model = Word
		fields = []