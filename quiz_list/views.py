import requests, json, shlex, ast
from collections import OrderedDict
from .models import QuizList, Word
from uauth.models import CustomUser
from .forms import QuizListDisplayForm, WordForm
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.http import Http404
from django.shortcuts import render

class QuizListView(ListView):
	model = QuizList
	template_name = "quiz_list/quizlist.html"

	def get_queryset(self):
		return self.model.objects.filter(user_fk = self.request.user)

class AddQuizView(FormView):
	template_name = "quiz_list/addquiz.html"
	form_class = QuizListDisplayForm
	success_url = reverse_lazy("customize_word")

	def post(self, request, *args, **kwargs):
		form = self.get_form()
		if (form.is_valid()):
			form_values = {
				'quiz_name': form.cleaned_data.get('quiz_name'),
				'time_limit': form.cleaned_data.get('time_limit'),
				'quiz_language': form.cleaned_data.get('quiz_language'),
				'word_list': form.cleaned_data.get('word_list')
			}
			cnt = QuizList.objects.filter(quiz_name = form_values['quiz_name']).count()
			list_word_cnt = len(list(OrderedDict.fromkeys(shlex.split(form_values['word_list']))))
			if cnt != 0:
				form.add_error(None, "Quiz name already existed")
				return self.form_invalid(form)

			if list_word_cnt > 10:
				form.add_error(None, "Too many words")
				return self.form_invalid(form)

			request.session['form_values'] = form_values
			return self.form_valid(form)
		else:
			return self.form_invalid(form)



class CustomizeWordView(FormView):
	template_name = "quiz_list/customize_word.html"
	form_class = WordForm
	success_url = reverse_lazy("quizlist")
	form_values = {}
	URL = 'https://api.dictionaryapi.dev/api/v2/entries/'#'<language_code>/<word>'

	def get(self, request, *args, **kwargs):
		try:
			self.form_values = request.session['form_values']
		except:
			raise Http404

		return super().get(self, args, kwargs)

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)

		list_word = list(OrderedDict.fromkeys(shlex.split(self.form_values['word_list'])))
		language_code = self.form_values['quiz_language']

		data['list_of_words'] = []

		for mword in list_word:
			response = requests.get(self.URL + language_code + '/' + mword)
			fetched_data = response.json()
			if (type(fetched_data) is dict):
				data['list_of_words'].append({'word': mword, 'meanings': []})
			else:
				data['list_of_words'].append(fetched_data[0])



		for word in data['list_of_words']:
			for meanings in word['meanings']:
				for definition in meanings['definitions']:
					definition['checkbox_val'] = {'m_word': word['word'],
												  'part_of_speech': meanings['partOfSpeech'],
												  'word_definition': definition['definition']}


		return data

	def post(self, request, *args, **kwargs):
		# TODO: undefined bugs, variable lost value
		checked_box = request.POST.getlist('checked-definition')
		self.form_values = request.session['form_values']

		if len(checked_box) == 0:
			t_form = self.get_form()
			t_form.add_error(None, "empty")
			return self.form_invalid(t_form)


		word_list = []
		for i in checked_box:
			i = ast.literal_eval(i)
			if (i['m_word'] not in word_list):
				word_list.append(i['m_word'])

		quiz_name = self.form_values['quiz_name']
		time_limit = self.form_values['time_limit']
		quiz_language = self.form_values['quiz_language']
		words_count = len(word_list)
		questions_count = len(checked_box)

		current_username = request.user.username
		userModel = CustomUser.objects.get(username=current_username)

		newQuizList = QuizList(user_fk = userModel,
							   quiz_name = quiz_name,
							   time_limit = time_limit,
							   words_count = words_count,
							   quiz_language = quiz_language,
							   questions_count = questions_count)

		newQuizList.save()

		for i in checked_box:
			i = ast.literal_eval(i)
			newWord = Word(quiz_id = newQuizList,
						   m_word = i['m_word'],
						   word_definition = i['word_definition'],
						   part_of_speech = i['part_of_speech'])
			newWord.save()

		request.session.pop('form_values', None)
		return super().post(self, request, args, kwargs)
