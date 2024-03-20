from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Theme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Test(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.ManyToManyField(Theme, null=True, blank=True)
    description = models.TextField(max_length=512)

    def __str__(self):
        return f'{self.name}'


class Question(models.Model):
    text = models.TextField(max_length=500)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.text[:25]}...' if len(self.text) > 25 else self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    right = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.right} {self.text[:10]}'
