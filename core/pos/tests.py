
from django.test import TestCase
from django.urls import reverse

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
