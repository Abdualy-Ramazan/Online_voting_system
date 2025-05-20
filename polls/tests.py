from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from polls.models import Poll, Choice, Vote
from django.utils import timezone
from datetime import timedelta

class PollsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.poll = Poll.objects.create(
            question="Ваш любимый цвет?",
            end_date=timezone.now() + timedelta(days=1),
            allow_multiple_choices=False,
            author=self.user
        )
        self.choice1 = Choice.objects.create(poll=self.poll, choice_text='Синий')
        self.choice2 = Choice.objects.create(poll=self.poll, choice_text='Зелёный')

    def test_register_login_logout(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302)

        login = self.client.login(username='newuser', password='newpassword123')
        self.assertTrue(login)

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_vote_once(self):
        self.client.login(username='testuser', password='testpass123')
        vote_url = reverse('vote', args=[self.poll.id])

        # Первое голосование
        response1 = self.client.post(vote_url, {'choice': self.choice1.id}, follow=True)
        self.assertContains(response1, "Спасибо за голос!")

        # Повторное голосование
        response2 = self.client.post(vote_url, {'choice': self.choice2.id}, follow=True)
        self.assertContains(response2, "Вы уже голосовали")

    def test_vote_requires_login(self):
        vote_url = reverse('vote', args=[self.poll.id])
        response = self.client.post(vote_url, {'choice': self.choice1.id})
        self.assertEqual(response.status_code, 302)  # Redirect to login
