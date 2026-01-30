from django.urls import path
# from . import views # 後でビューを作成した際にコメントを外します

# api/ に続くURLパターンを定義します
urlpatterns = [
    # 体調ログ (ConditionLog) 関連
    # path('condition-logs/', views.condition_log_list_create, name='condition_log_list_create'), # ログインユーザーの体調ログ一覧取得・新規作成
    # path('condition-logs/<int:pk>/', views.condition_log_detail, name='condition_log_detail'), # 特定の体調ログの詳細取得・更新・削除
    # path('condition-logs/<str:date>/', views.condition_log_by_date, name='condition_log_by_date'), # 特定の日付の体調ログを取得・更新・削除 (例: /api/condition-logs/2023-01-01/)

    # 運動メニュー (ExerciseMenu) 関連
    # path('exercise-menus/', views.exercise_menu_list, name='exercise_menu_list'), # 運動メニュー一覧取得
    # path('exercise-menus/<int:pk>/', views.exercise_menu_detail, name='exercise_menu_detail'), # 特定の運動メニュー詳細取得

    # ルーティン (Routine) 関連
    # path('routines/', views.routine_list_create, name='routine_list_create'), # ログインユーザーのルーティン一覧取得・新規追加
    # path('routines/<int:pk>/', views.routine_detail, name='routine_detail'), # 特定のルーティン項目を削除
]
