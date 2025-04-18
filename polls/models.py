from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100, default="anonymous")  # <--- добавили default
    vote_choice = models.CharField(max_length=200)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote by {self.user_name} on {self.poll.question}"


class Rating(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100, default="anonymous")  # <--- тоже добавим здесь
    rating_value = models.IntegerField(default=0)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.user_name} on {self.poll.question}"
