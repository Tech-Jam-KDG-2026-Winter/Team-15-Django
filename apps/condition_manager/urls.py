from django.urls import path
# from . import views # 後でビューを作成した際にコメントを外します

# api/ に続くURLパターンを定義します
urlpatterns = [
    #これは実装例です

    #  # 【廣田さん担当】体調ログ保存＆メニュー提案API
    # path('recommend/', views.recommend_exercise_view, name='recommend_exercise'),

    # # 【廣田さん担当】運動メニュー詳細API (追加)
    # path('exercises/<int:pk>/', views.exercise_detail_view, name='exercise_detail'),

    # # 【鈴木さん担当】ルーティン管理API
    # path('routines/<int:exercise_id>/', views.routine_manage_view, name='manage_routine'),

    # # 【鈴木さん担当】履歴取得API
    # path('history/', views.history_list_view, name='history_list'),

    # # 【鈴木さん担当】ルーティン一覧取得API (追加)
    # path('routines/', views.routine_list_view, name='routine_list'),

    # # 【鈴木さん担当】運動メニュー一覧・検索API (追加)
    # path('exercises/', views.exercise_list_view, name='exercise_list'),
]
