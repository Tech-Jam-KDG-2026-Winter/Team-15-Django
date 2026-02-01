from django.urls import path
from . import views

# api/ に続くURLパターンを定義します
urlpatterns = [
    # 体調ログ保存＆メニュー提案API
    path('recommend/', views.recommend_exercise_view, name='recommend_exercise'),

    # ここに将来的なエンドポイントを追加できます
    # path('exercises/<int:pk>/', views.exercise_detail_view, name='exercise_detail'),
    # path('routines/<int:exercise_id>/', views.routine_manage_view, name='manage_routine'),
    # path('history/', views.history_list_view, name='history_list'),
]
