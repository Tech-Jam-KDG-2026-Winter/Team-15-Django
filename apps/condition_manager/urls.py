from django.urls import path
from . import views # 後でビューを作成した際にコメントを外します

# api/ に続くURLパターンを定義します
urlpatterns = [
    # 体調ログ保存＆メニュー提案API
    path('recommend/', views.recommend_exercise_view, name='recommend_exercise'),

    # # 【鈴木さん担当】運動メニュー一覧・検索API (追加)
    # path('exercises/', views.exercise_list_view, name='exercise_list'),

    # ルーティン管理API (追加/削除)
    path('routines/<int:exercise_id>/', views.routine_manage_view, name='manage_routine'),

    # 履歴取得API
    path('history/', views.history_list_view, name='history_list'),

    # ルーティン一覧取得API
    path('routines/', views.routine_list_view, name='routine_list'),

    # 運動メニュー詳細API
    path('exercises/<int:pk>/', views.exercise_detail_view, name='exercise_detail'),


    path('api/exercises/', views.exercise_list_view, name='exercise-list'),
    path('api/exercises/<int:pk>/', views.exercise_detail_view, name='exercise-detail'),

]
