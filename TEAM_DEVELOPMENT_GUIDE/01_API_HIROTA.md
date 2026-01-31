# 【廣田さんへ：体調ログ・メニュー提案API担当】

**あなたの役割**
ユーザーの体調を受け取り、体調ログを保存しつつ、運動メニューを提案するAPI (`/api/recommend/`) のロジック部分を担当していただきます。

**担当する主なファイル**
*   `apps/condition_manager/views.py` (特に `recommend_exercise_view` 関数)
*   `apps/condition_manager/urls.py` (関連パス)
*   `apps/condition_manager/serializers.py` (必要なシリアライザの確認)

## 考えるべきポイント
1.  **JSON入出力**: フロントエンドからはJSON形式で体調データが送られてきます (`request.data`)。あなたはそのデータを受け取り、提案結果もJSON形式で返却します (`Response` オブジェクト)。
2.  **重み付けロジック**: `recommend_exercise_view` 内の `calculate_score` 関数（またはそのロジックを直接埋め込む）を、よりユーザーの状態に合わせた最適な提案ができるように設計・実装してください。どのタグにどれくらいの点数を与えるか、どの条件を優先するかなど、あなたのアイデアを活かしてください。
3.  **タグ設計**: `ExerciseMenu` と `Tag` が適切に紐付けられていることが前提となります。効果的な提案のために、どのようなタグが必要か、管理サイトで試しながら考えてみてください。
4.  **エラーハンドリング**: 無効な入力値が来た場合（数値以外など）や、提案するメニューが全く見つからなかった場合の適切なレスポンスを考慮してください。

---

## 実装の骨子

### `apps/condition_manager/views.py`

```python
# 一部のみ。必要なインポートは追記してください。
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import ConditionLog, ExerciseMenu, Tag
from .serializers import ExerciseMenuSerializer # 提案メニューのシリアライザ

# TODO: calculate_score 関数を、あなたの考える最適な重み付けロジックで実装してください。
#       引数: menu (ExerciseMenuオブジェクト), fatigue (int), mood (int), concern (str)
#       戻り値: score (int)
def calculate_score(menu: ExerciseMenu, fatigue: int, mood: int, concern: str) -> int:
    score = 0
    menu_tags = [tag.name for tag in menu.tags.all()] # メニューに紐づくタグ名リスト

    # 悩みの解決 (例: '肩' と '#肩こり解消' が一致したら大きく加点)
    # 疲れレベル (例: 高疲労時は '高疲労時向け' に加点、筋トレ系は減点)
    # 気分レベル (例: 気分が落ち込んでいる時は '気分転換' に加点)

    # TODO: ここにスコア計算ロジックを記述してください。
    # 現在のロジックは非常にシンプルなので、もっと複雑にしてもOKです。
    # 例: if '肩' in concern and '肩こり解消' in menu_tags: score += 50
    # 例: if fatigue >= 4 and '高疲労時向け' in menu_tags: score += 30


    # 目安:
    # ・最低でも「疲れ」「気分」「悩み」のうち2つはスコア計算に使うこと
    # ・条件分岐は3〜5個程度あれば十分です


    return score

@api_view(['POST'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def recommend_exercise_view(request):

    "ここではロジックの例を記載していますが、ユーザーの入力に合わせた提案をより正確にするロジックを廣田さんに考え、作っていただければと思います"

    """
    体調ログを保存し、運動メニューを提案するAPI。

    【レスポンス仕様】
    このAPIは、以下の2パターンのJSONを返します。

    1. 通常時（おすすめメニューがある場合）
       - 配列（list）を返却
       - 各要素は ExerciseMenuSerializer の形式

       例:
       [
         {
           "id": 1,
           "name": "肩回しストレッチ",
           "description": "...",
           ...
         }
       ]

    2. 休息提案時（おすすめメニューが見つからない場合）
       - オブジェクト（dict）を返却
       - rest_suggestion = true が含まれる

       例:
       {
         "message": "今日は無理せず休みましょう",
         "rest_suggestion": true,
         "recommended_menus": []
       }

    フロントエンドでは `rest_suggestion` の有無で分岐する想定。
    """

    # TODO: request.data(main.jsで、htmlのフォームからjson形式なったdata) から疲れレベル、気分レベル、悩みを安全に取得してください。
    fatigue = request.data.get('fatigue_level')
    mood = request.data.get('mood_level')
    concern = request.data.get('body_concern', '')

    # TODO: 取得した入力値のバリデーションを強化してください。
    #       例えば、int()変換エラーや、1-5の範囲外の値をチェック。
    try:
        fatigue = int(fatigue) if fatigue is not None else None
        mood = int(mood) if mood is not None else None
        if not (1 <= fatigue <= 5 and 1 <= mood <= 5):
            return Response({"error": "疲れレベルと気分レベルは1から5の間で入力してください。"}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({"error": "疲れレベルと気分レベルは数値で入力してください。"}, status=status.HTTP_400_BAD_REQUEST)

    # TODO: ConditionLog をデータベースに保存してください。
    #       user=request.user を使うことで、ログインユーザーに紐付けられます。
    ConditionLog.objects.create(
        user=request.user,
        fatigue_level=fatigue,
        mood_level=mood,
        body_concern=concern
        # log_dateはモデルのdefault=timezone.nowで自動設定されます
    )

    # 全ての運動メニューを取得（タグを効率的に取得できるようにprefetch_relatedを使うと良いでしょう）
    all_menus = ExerciseMenu.objects.all().prefetch_related('tags')
    scored_menus = []

    for menu in all_menus:
        score = calculate_score(menu, fatigue, mood, concern) # TODO: calculate_scoreを完成させる
        if score > 0: # スコアが0より大きいメニューだけを候補とする
            scored_menus.append({'menu': menu, 'score': score})

    # スコアの高い順にソートし、最大3件選ぶ
    scored_menus.sort(key=lambda x: x['score'], reverse=True)
    recommended_menus_objects = [item['menu'] for item in scored_menus[:3]]

    # TODO: 提案する運動が見つからなかった場合のレスポンスを設計してください。
    #       このサンプルでは「休息を促すメッセージ」を返すロジックになっています。
    if not recommended_menus_objects:
        return Response({
            "message": "あなたに最適なメニューが見つかりませんでした。今日は無理せず休息をとりましょう。軽い呼吸法や瞑想もおすすめです。",
            "recommended_menus": [],
            "rest_suggestion": True
        }, status=status.HTTP_200_OK)

    # 選ばれた運動メニューをJSON形式に変換してフロントエンドに返す
    serializer = ExerciseMenuSerializer(recommended_menus_objects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
```

### `apps/condition_manager/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_exercise_view, name='recommend_exercise'),
    # TODO: 必要であれば、他のAPIもここに追加してください
]
```

※補足（重要）
このAPIは最終的にフロントエンドの非同期通信から呼ばれますが、
現時点では「API単体での完成」を目標にしてください。

・curl / Postman / Django REST Frameworkのブラウザ表示で
  正しいJSONレスポンスが返ればOKです。
・画面上で動かなくても問題ありません。


