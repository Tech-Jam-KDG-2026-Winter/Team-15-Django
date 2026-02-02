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

from django.db.models import Q # 検索フィルタリングにQオブジェクトを使う場合
from django.core.paginator import Paginator, EmptyPage

from .models import ConditionLog, ExerciseMenu, Routine, Tag
from .serializers import ConditionLogSerializer, RoutineSerializer, ExerciseMenuSerializer

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def routine_manage_view(request, exercise_id: int):
    """
    特定の運動メニューをルーティンに追加・削除するAPI
    """
    # exercise_id が存在しない場合の適切なエラーレスポンス
    try:
        exercise = ExerciseMenu.objects.get(pk=exercise_id)
    except ExerciseMenu.DoesNotExist:
        return Response(
            {"error": f"運動メニューID: {exercise_id} が見つかりません。"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'POST':
        # 既に登録済みの場合は別のメッセージを返す
        routine, created = Routine.objects.get_or_create(user=request.user, exercise=exercise)
        serializer = RoutineSerializer(routine)
        
        if created:
            # 新規作成時：メッセージとルーティンデータを返す
            return Response({
                "message": "ルーティンに追加しました",
                "routine": serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            # 既に存在する場合：メッセージと既存のルーティンデータを返す
            return Response({
                "message": "この運動メニューは既にルーティンに登録されています。",
                "routine": serializer.data
            }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # 削除対象がない場合はエラーメッセージ
        deleted_count, _ = Routine.objects.filter(user=request.user, exercise=exercise).delete()
        
        if deleted_count == 0:
            return Response(
                {"error": f"ルーティンに運動メニューID: {exercise_id} が登録されていないため削除できません。"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみ
def history_list_view(request):
    """
    ログインユーザーの過去の体調ログ履歴を一覧で返すAPI
    並び順: 新しい順
    件数制限: 20件、5件ごとにページング
    """
    # パラメータからページ番号を取得
    page_number = request.GET.get('page', 1)
    
    # 全履歴を取得（新しい順）
    logs = ConditionLog.objects.filter(user=request.user).order_by('-log_date', '-created_at')
    
    # ページネーション設定: 1ページあたり5件、最大20件まで表示
    paginator = Paginator(logs[:20], 5)  # 最大20件に制限し、5件ごとにページング
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        return Response(
            {"error": "指定されたページが存在しません。"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ConditionLogSerializer(page_obj, many=True)
    
    return Response({
        "count": paginator.count,  # 総件数
        "total_pages": paginator.num_pages,  # 総ページ数
        "current_page": page_obj.number,  # 現在のページ番号
        "results": serializer.data  # データ
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみ
def routine_list_view(request):
    """
    ログインユーザーのルーティン一覧を返すAPI
    並び順: 閲覧数順（view_countが多い順）
    件数制限: 20件、5件ごとにページング
    """
    # クエリパラメータからページ番号を取得
    page_number = request.GET.get('page', 1)
    
    # 全ルーティンを取得（閲覧数が多い順、同じ場合は追加が新しい順）
    routines = Routine.objects.filter(user=request.user).order_by('-view_count', '-added_at')
    
    # ページネーション設定: 1ページあたり5件、最大20件まで表示
    paginator = Paginator(routines[:20], 5)  # 最大20件に制限し、5件ごとにページング
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        return Response(
            {"error": "指定されたページが存在しません。"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = RoutineSerializer(page_obj, many=True)
    
    return Response({
        "count": paginator.count,  # 総件数
        "total_pages": paginator.num_pages,  # 総ページ数
        "current_page": page_obj.number,  # 現在のページ番号
        "results": serializer.data  # データ
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def exercise_detail_view(request, pk: int): # URLから渡されるIDをpkとして受け取る
    """
    特定の運動メニューの詳細情報を返すAPI
    """
    # 運動メニューが見つからない場合の適切なエラーレスポンス
    try:
        exercise = ExerciseMenu.objects.get(pk=pk)
    except ExerciseMenu.DoesNotExist:
        return Response(
            {"error": f"運動メニューID: {pk} が見つかりません。"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = ExerciseMenuSerializer(exercise)
    return Response(serializer.data, status=status.HTTP_200_OK)

