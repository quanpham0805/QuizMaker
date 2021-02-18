import requests, json, shlex, ast, random
from collections import OrderedDict
from .models import QuizList, Word
from uauth.models import CustomUser
from .forms import QuizListDisplayForm, WordForm
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.http import Http404
from django.shortcuts import redirect, render

def finishQuiz(request):
	if request.method == "GET":
		raise Http404("You are not allowed to access this site")
	else:
		checked_box = [ast.literal_eval(i) for i in request.POST.getlist('checked-box')]
		all_choices = [ast.literal_eval(i) for i in request.POST.getlist('selection_list')]
		quiz_name = request.POST.get('quiz_name')
		quiz_max = 0
		quiz_object = QuizList.objects.filter(user_fk = request.user, quiz_name = quiz_name)
		quiz_id = 0
		for i in quiz_object.all():
			quiz_id = i.id
			time_limit = i.time_limit
			quiz_max = i.questions_count

		word_list = Word.objects.filter(quiz_id=quiz_id)

		correct_answer_group = {}
		for val in word_list.all():
			key1 = val.word_definition
			key2 = val.m_word + val.part_of_speech
			correct_answer_group[key1] = {}
			correct_answer_group[key1][key2] = 1

		# selection group: dict of {definition, {word + pos, 0}}
		selection_group = {}
		for i in all_choices:
			if i[0] not in selection_group:
				selection_group[i[0]] = {}
			if i[1] + i[2] not in selection_group[i[0]]:
				selection_group[i[0]][i[1] + i[2]] = 0
			if i[0] in correct_answer_group and i[1] + i[2] in correct_answer_group[i[0]] and correct_answer_group[i[0]][i[1] + i[2]] == 1:
				selection_group[i[0]][i[1] + i[2]] += 1

		for i in checked_box:
			selection_group[i[0]][i[1] + i[2]] -= 1

		total_correct = 0;
		for key1 in selection_group:
			ans = True
			for key2 in selection_group[key1]:
				if selection_group[key1][key2] != 0:
					ans = False

			if ans:
				total_correct += 1

		# print(total_correct)
		for i in quiz_object.all():
			best_att = i.best_attempt
			if (best_att == "N/A"):
				i.best_attempt = str(total_correct) + "/" + str(quiz_max)
				i.save()
			else:
				old_score = best_att.split('/')[0]
				if (int(old_score) < total_correct):
					i.best_attempt = str(total_correct) + "/" + str(quiz_max)
					i.save()

		return render(request, template_name="quiz_list/finishquiz.html", context={'total_correct': total_correct, 'total': quiz_max})

def generate_choice(list_of_choice, cur_choice):
	ans_list = []
	ans_list.append(cur_choice)
	list_of_choice = [i for i in list_of_choice if i != cur_choice]
	while (len(ans_list) < 4):
		if (len(list_of_choice) == 0):
			ans_list.append(ans_list[-1])
		else:
			cur_choice = random.choice(list_of_choice)
			ans_list.append(cur_choice)
			list_of_choice = [i for i in list_of_choice if i != cur_choice]

	random.shuffle(ans_list)
	return ans_list


def doQuiz(request):
	if request.method == "GET":
		raise Http404("You are not allowed to access this site")
	else:
		quiz_name = request.POST.getlist('quiz_to_do')[0]
		# print(quiz_name)
		quiz_object = QuizList.objects.filter(user_fk = request.user, quiz_name = quiz_name)
		quiz_id = 0
		time_limit = 0
		for i in quiz_object.all():
			quiz_id = i.id
			time_limit = i.time_limit

		word_list = Word.objects.filter(quiz_id=quiz_id)
		m_word_list = []
		definition_list = []
		for val in word_list.all():
			temp_var = []
			temp_var.append(val.m_word)
			temp_var.append(val.part_of_speech)
			m_word_list.append(temp_var)
			definition_list.append(val.word_definition)

		question_list = []
		z = 0
		for i in range(len(m_word_list)):
			choice_list_value = generate_choice(m_word_list, m_word_list[i])
			choice_list = []
			for j in choice_list_value:
				clv = j.copy()
				clv.insert(0, definition_list[i])
				temp_dict = {'choice_list_value': clv, 'choice_list': j[0] + ' (' + j[1] + ')', 'id_list': "selection" + str(z)}
				choice_list.append(temp_dict)
				z += 1

			qdict = {'definition': definition_list[i], 'selection': choice_list}
			question_list.append(qdict)

		# print(m_word_list)
		# print(definition_list)
		# print(question_list)
		return render(request, template_name = "quiz_list/doquiz.html", context = {'time_limit': time_limit, 'question_list': question_list, 'quiz_name': quiz_name})

def deleteWord(request):
	if request.method == "GET":
		raise Http404("You are not allowed to access this site")
	else:
		quiz_name = request.POST.getlist('selected_quiz')[0]
		QuizList.objects.filter(user_fk = request.user, quiz_name = quiz_name).delete()
		return redirect("quizlist")

class QuizListView(ListView):
	model = QuizList
	template_name = "quiz_list/quizlist.html"

	def get_queryset(self):
		if self.request.user.is_authenticated:
			return self.model.objects.filter(user_fk = self.request.user)
		return None

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
			cnt = QuizList.objects.filter(user_fk = self.request.user, quiz_name = form_values['quiz_name']).count()
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
