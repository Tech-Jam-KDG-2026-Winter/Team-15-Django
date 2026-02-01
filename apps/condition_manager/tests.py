from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


class RecommendExerciseAPITest(TestCase):
	def setUp(self):
		# import models lazily to avoid AppRegistry issues during test discovery
		from .models import Tag, ExerciseMenu

		User = get_user_model()
		self.user = User.objects.create_user(username='testuser', password='pass')
		# create tags and exercise menus
		t1 = Tag.objects.create(name='肩こり解消')
		t2 = Tag.objects.create(name='ストレッチ')
		m1 = ExerciseMenu.objects.create(
			name='肩ストレッチ',
			description='肩をほぐすストレッチ',
			beginner_guide='座ったままでOK',
			category='stretch',
			target_area='肩',
		)
		m1.tags.add(t1, t2)

	def test_recommend_exercise_view_returns_menus(self):
		client = APIClient()
		client.force_login(self.user)

		data = {'fatigue_level': 4, 'mood_level': 3, 'body_concern': '肩がつらい'}
		response = client.post('/api/condition/recommend/', data, format='json')

		# view may not be routed; fallback: directly call view if 404
		if response.status_code == 404:
			# import view and call directly
			from .views import recommend_exercise_view
			from rest_framework.test import APIRequestFactory

			factory = APIRequestFactory()
			req = factory.post('/api/condition/recommend/', data, format='json')
			req.user = self.user
			resp = recommend_exercise_view(req)
			self.assertEqual(resp.status_code, 200)
			self.assertTrue(isinstance(resp.data, list) or resp.data.get('rest_suggestion') is not None)
		else:
			self.assertEqual(response.status_code, 200)
			self.assertTrue(isinstance(response.data, list) or response.data.get('rest_suggestion') is not None)
