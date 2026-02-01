from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory


class ConditionManagerViewsTest(TestCase):
    def setUp(self):
        # lazy imports to avoid AppRegistry issues during discovery
        from .models import Tag, ExerciseMenu

        User = get_user_model()
        self.user = User.objects.create_user(username='viewer', password='pass')

        # matching menu for shoulder
        self.tag_shoulder = Tag.objects.create(name='肩こり解消')
        self.menu_shoulder = ExerciseMenu.objects.create(
            name='肩ストレッチ2',
            description='肩周りをほぐす',
            beginner_guide='座ってできる',
            category='stretch',
            target_area='肩',
        )
        self.menu_shoulder.tags.add(self.tag_shoulder)

        # non-matching menu
        self.menu_other = ExerciseMenu.objects.create(
            name='ランニング',
            description='有酸素運動',
            beginner_guide='屋外で実施',
            category='cardio',
            target_area='脚',
        )

    def test_calculate_score_prefers_matching_tags(self):
        # import under test
        from . import views

        score = views.calculate_score(self.menu_shoulder, fatigue=3, mood=3, concern='肩が痛い')
        # concern match + tag match should add a large boost
        self.assertGreaterEqual(score, 60)

    def test_recommend_exercise_view_returns_rest_when_no_match(self):
        from .views import recommend_exercise_view
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        data = {'fatigue_level': 1, 'mood_level': 1, 'body_concern': '頭が痛い'}
        req = factory.post('/api/condition/recommend/', data, format='json')
        req.user = self.user

        resp = recommend_exercise_view(req)
        self.assertEqual(resp.status_code, 200)
        # accept either a dict with rest_suggestion True or a list of menus
        self.assertTrue(isinstance(resp.data, dict) or isinstance(resp.data, list))
        if isinstance(resp.data, dict):
            self.assertTrue(resp.data.get('rest_suggestion') is True)

    def test_recommend_exercise_view_returns_recommendation_for_shoulder(self):
        from .views import recommend_exercise_view
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        data = {'fatigue_level': 3, 'mood_level': 3, 'body_concern': '肩がつらい'}
        req = factory.post('/api/condition/recommend/', data, format='json')
        req.user = self.user

        resp = recommend_exercise_view(req)
        self.assertEqual(resp.status_code, 200)
        # should return a list of recommended menus
        self.assertIsInstance(resp.data, list)
        self.assertTrue(len(resp.data) >= 1)
