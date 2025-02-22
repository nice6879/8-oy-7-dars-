from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    name = models.CharField(max_length=100) 
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    
    def __str__(self):
        return self.name
    
    @property
    def questions(self):
        return Question.objects.filter(quiz=self)
    
    @property
    def questions_count(self):
        return Question.objects.filter(quiz=self).count()

class Question(models.Model):
    name = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    @property
    def options(self):
        return Option.objects.filter(question=self)

    @property
    def correct_option(self):
        return Option.objects.filter(question=self, correct=True).first()

class Option(models.Model):
    name = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.correct:
            Option.objects.filter(question=self.question).update(correct=False)
            self.correct = True
        super(Option, self).save(*args, **kwargs)

class Answer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_late = models.BooleanField()

    def __str__(self):
        return f"{self.author.username} -> {self.quiz.name}"
    
    def save(self, *args, **kwargs):
        time = self.end_time - self.start_time
        self.is_late = time.total_seconds() / 60 > self.quiz.amount
        super(Answer, self).save(*args, **kwargs)

class AnswerDetail(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_choice = models.ForeignKey(Option, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if AnswerDetail.objects.filter(answer=self.answer, question=self.question).exists():
            raise ValueError("Bu savolga javob berilgan")
        super(AnswerDetail, self).save(*args, **kwargs)

    @property
    def is_correct(self):
        return self.user_choice == self.question.correct_option
