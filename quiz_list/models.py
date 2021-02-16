from django.db import models

# Create your models here.

class QuizList(models.Model):
	user_fk = models.ForeignKey('uauth.CustomUser', on_delete = models.CASCADE)
	quiz_name = models.CharField(max_length = 50)
	time_limit = models.PositiveIntegerField()
	words_count = models.PositiveIntegerField(default = 0)
	quiz_language = models.CharField(max_length = 2)
	questions_count = models.PositiveIntegerField(default = 0)
	best_attempt = models.CharField(default="N/A", max_length = 10)



class Word(models.Model):
	quiz_id = models.ForeignKey(QuizList, on_delete = models.CASCADE)
	m_word = models.CharField(max_length=75)
	word_definition = models.TextField()
	part_of_speech = models.CharField(max_length=20)
	example = models.TextField()
	synonyms = models.TextField()
