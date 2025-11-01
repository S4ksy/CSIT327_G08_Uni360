
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Building

class SignupViewTests(TestCase):
	def test_valid_email_is_accepted(self):
		response = self.client.post(reverse('signup'), {
			'username': 'testuser',
			'email': 'jamesandrew.magdales@cit.edu',
			'password': 'testpass123',
			'school_id': '23-6555-528'
		})
		# Should redirect to login page (status code 302)
		self.assertEqual(response.status_code, 302)

class MapViewTests(TestCase):
	def setUp(self):
		# Create a test user
		self.user = User.objects.create_user(username='testuser', password='testpass123')
		# Create test buildings
		Building.objects.create(name='Test Building 1', description='Description 1', latitude=10.31672, longitude=123.89071)
		Building.objects.create(name='Test Building 2', description='Description 2', latitude=10.31772, longitude=123.89171)

	def test_map_view_requires_login(self):
		response = self.client.get(reverse('map'))
		self.assertEqual(response.status_code, 302)  # Redirect to login

	def test_map_view_with_login(self):
		self.client.login(username='testuser', password='testpass123')
		response = self.client.get(reverse('map'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'buildings-data')  # Check if buildings data is in the response
		self.assertContains(response, 'Test Building 1')
		self.assertContains(response, 'Test Building 2')
