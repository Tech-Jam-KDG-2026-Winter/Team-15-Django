# 【鈴木さんへ：データ管理・履歴・ルーティンAPI担当】

**あなたの役割**
ユーザーのデータ管理（履歴、ルーティン）と、運動メニュー詳細・一覧のAPIを提供するバックエンドロジックを担当していただきます。JavaScriptコードを直接書く必要はありません。

**担当する主なファイル**
*   `apps/condition_manager/views.py` (`routine_manage_view`, `history_list_view`, `exercise_detail_view`, 関数)
*   `apps/condition_manager/urls.py` (関連パス)
*   `apps/condition_manager/serializers.py` (必要なシリアライザの確認)

## 考えるべきポイント
1.  **APIの設計**: URL構造、リクエストの受け取り方、JSONでのレスポンス形式、HTTPステータスコード（成功時の200 OK、作成時の201 Created、削除時の204 No Content、見つからない時の404 Not Found、エラー時の400 Bad Requestなど）を意識してください。
2.  **データの取得・操作**: `request.user` を使ってログインユーザーに紐づくデータのみを操作するようにしてください。
3.  **エラーハンドリング**: 存在しないIDが指定された場合 (`.get()` で `DoesNotExist` エラーが発生した場合など) や、不適切なリクエストが来た場合の適切なエラーレスポンスを設計してください。
4.  **並び順・件数制限**: 履歴やルーティンの一覧表示では、どの順序で、どのくらいの件数を返すのがユーザーにとって最適か考慮してください。（例: 最新のものが上に来るように `order_by('-log_date')` を使う、ページングを導入するなど）

---

## 実装の骨子

### `apps/condition_manager/views.py`

```python
# 一部のみ抜粋。必要なインポートは追記してください。
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q # 検索フィルタリングにQオブジェクトを使う場合

from .models import ConditionLog, ExerciseMenu, Routine, Tag
from .serializers import ConditionLogSerializer, RoutineSerializer, ExerciseMenuSerializer

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def routine_manage_view(request, exercise_id: int):
    """
    特定の運動メニューをルーティンに追加・削除するAPI
    """
    # TODO: exercise_id が存在しない場合の適切なエラーレスポンスを設計・実装する
    try:
        exercise = ExerciseMenu.objects.get(pk=exercise_id)
    except ExerciseMenu.DoesNotExist:
        return Response({"error": "指定された運動メニューが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # TODO: 既に登録済みの場合の挙動（エラーにするか、何もしないか）をどうするか決める
        #       現在は get_or_create で重複登録を防いでいます。その挙動で良いか確認。
        Routine.objects.get_or_create(user=request.user, exercise=exercise)
        return Response({"message": "ルーティンに追加しました"}, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        # TODO: 削除対象がない場合のレスポンスをどうするか決める
        #       現在は単に削除を試みていますが、その挙動で良いか確認。
        Routine.objects.filter(user=request.user, exercise=exercise).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def history_list_view(request):
    """
    ログインユーザーの過去の体調ログ履歴を一覧で返すAPI
    """
    # TODO: 並び順の決定（デフォルトは最新が上）
    # TODO: 件数制限やページング（取得するデータの数を制限）をどうするか設計する
    logs = ConditionLog.objects.filter(user=request.user).order_by('-log_date', '-created_at')
    serializer = ConditionLogSerializer(logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def routine_list_view(request):
    """
    ログインユーザーのルーティン一覧を返すAPI
    """
    # TODO: 並び順の決定（デフォルトは追加が新しい順）
    # TODO: 件数制限やページングをどうするか設計する
    routines = Routine.objects.filter(user=request.user).order_by('-added_at')
    serializer = RoutineSerializer(routines, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def exercise_detail_view(request, pk: int): # URLから渡される主キー (ID) をpkとして受け取る
    """
    特定の運動メニューの詳細情報を返すAPI
    """
    # TODO: 運動メニューが見つからない場合の適切なエラーレスポンスを設計・実装する
    try:
        exercise = ExerciseMenu.objects.get(pk=pk)
    except ExerciseMenu.DoesNotExist:
        return Response({"error": "指定された運動メニューが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExerciseMenuSerializer(exercise)
    return Response(serializer.data, status=status.HTTP_200_OK)
```

### `apps/condition_manager/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    # ルーティン管理API (追加/削除)
    path('routines/<int:exercise_id>/', views.routine_manage_view, name='manage_routine'),

    # 履歴取得API
    path('history/', views.history_list_view, name='history_list'),

    # ルーティン一覧取得API
    path('routines/', views.routine_list_view, name='routine_list'),

    # 運動メニュー詳細API
    path('exercises/<int:pk>/', views.exercise_detail_view, name='exercise_detail'),

    # ...他のAPIのURLに続く...
]
```
