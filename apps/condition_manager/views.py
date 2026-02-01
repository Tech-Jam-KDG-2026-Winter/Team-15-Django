from django.db.models import Prefetch
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ConditionLog, ExerciseMenu, Tag
from .serializers import ExerciseMenuSerializer


# ---- ここが肝：スコアリング（タグベース） ----
def calculate_score(menu: ExerciseMenu, fatigue: int, mood: int, concern: str) -> int:
    # ベース点（0件を減らすために少し入れる）
    score = 5

    tags_raw = [t.name for t in menu.tags.all()]
    # 「#」あり/なし揺れ対策
    tags = set()
    for n in tags_raw:
        if not n:
            continue
        tags.add(n)
        tags.add(n.lstrip("#"))

    concern = (concern or "").strip()

    def has_any(*names: str) -> bool:
        return any(n in tags for n in names)

    # 1) 悩み（部分一致） → かなり強く効かせる
    concern_map = {
        "肩": ("肩こり解消", "肩甲骨", "肩"),
        "首": ("首こり改善", "首", "首こり"),
        "腰": ("腰痛改善", "腰", "骨盤"),
        "目": ("眼精疲労", "目", "視界"),
        "脚": ("むくみ改善", "脚", "下半身"),
    }
    for key, wanted in concern_map.items():
        if key in concern:
            if has_any(*wanted):
                score += 60

    # 2) 疲れレベル
    if fatigue >= 4:
        # 高疲労 → 軽め優遇、筋トレ/高強度は減点
        if has_any("高疲労向け", "ストレッチ", "リラックス", "呼吸法", "軽め", "座ったまま"):
            score += 30
        if has_any("筋トレ", "高強度", "追い込み"):
            score -= 25
    elif fatigue <= 2:
        # 低疲労 → 筋トレ/有酸素もOK
        if has_any("筋トレ", "有酸素", "アクティブ"):
            score += 20
    else:
        # 3 あたりは中間
        if has_any("ストレッチ", "筋トレ"):
            score += 10

    # 3) 気分レベル
    if mood <= 2:
        # 気分低い → 気分転換/リフレッシュ系優遇
        if has_any("リフレッシュ", "気分転換", "呼吸法", "瞑想", "リラックス"):
            score += 25
    elif mood >= 4:
        # 気分高い → 達成感/筋トレも少し優遇
        if has_any("達成感", "筋トレ", "有酸素"):
            score += 10

    # 4) 継続性（やりやすいメニューを少し上げる）
    if has_any("初心者向け", "短時間", "座ったまま"):
        score += 10

    return max(score, 0)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recommend_exercise_view(request):
    """
    体調ログを保存し、運動メニューを最大3件提案するAPI
    - 通常: ExerciseMenu の配列
    - 提案なし: rest_suggestion: true のオブジェクト
    """

    # ---- 入力取得 ----
    fatigue = request.data.get("fatigue_level")
    mood = request.data.get("mood_level")
    concern = request.data.get("body_concern", "")

    # ---- バリデーション ----
    try:
        fatigue = int(fatigue)
        mood = int(mood)
    except (TypeError, ValueError):
        return Response(
            {"error": "fatigue_level と mood_level は整数(1-5)で指定してください。"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not (1 <= fatigue <= 5 and 1 <= mood <= 5):
        return Response(
            {"error": "fatigue_level と mood_level は 1〜5 の範囲で指定してください。"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if concern is None:
        concern = ""
    concern = str(concern).strip()

    # ---- ログ保存 ----
    ConditionLog.objects.create(
        user=request.user,
        fatigue_level=fatigue,
        mood_level=mood,
        body_concern=concern,
    )

    # ---- メニュー取得（タグもまとめて）----
    all_menus = ExerciseMenu.objects.all().prefetch_related(
        Prefetch("tags", queryset=Tag.objects.all())
    )

    scored = []
    for menu in all_menus:
        s = calculate_score(menu, fatigue, mood, concern)
        if s > 0:
            scored.append((s, menu))

    scored.sort(key=lambda x: x[0], reverse=True)
    recommended = [m for _, m in scored[:3]]

    # ---- 提案なし：休息レスポンス ----
    if not recommended:
        return Response(
            {
                "message": "あなたに最適なメニューが見つかりませんでした。今日は無理せず休息をとりましょう。",
                "rest_suggestion": True,
                "recommended_menus": [],
            },
            status=status.HTTP_200_OK,
        )

    # ---- 通常：メニュー配列 ----
    return Response(ExerciseMenuSerializer(recommended, many=True).data, status=status.HTTP_200_OK)
