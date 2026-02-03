# 一部のみ抜粋。必要なインポートは追記してください。
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
        # 既に登録済みの場合は別のメッセージを返す（B案）
        routine, created = Routine.objects.get_or_create(user=request.user, exercise=exercise)
        
        # ルーティンデータをシリアライズ
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
        # 削除対象がない場合は適切なエラーメッセージを返す
        deleted_count, _ = Routine.objects.filter(user=request.user, exercise=exercise).delete()
        
        if deleted_count == 0:
            return Response(
                {"error": f"ルーティンに運動メニューID: {exercise_id} が登録されていないため削除できません。"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def history_list_view(request):
    """
    ログインユーザーの過去の体調ログ履歴を一覧で返すAPI
    並び順: 新しい順
    件数制限: 20件、5件ごとにページング
    """
    # クエリパラメータからページ番号を取得（デフォルトは1ページ目）
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
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def routine_list_view(request):
    """
    ログインユーザーのルーティン一覧を返すAPI
    並び順: 閲覧数順（view_countが多い順）
    件数制限: 20件、5件ごとにページング
    """
    # クエリパラメータからページ番号を取得（デフォルトは1ページ目）
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
def exercise_list_view(request):
    """
    運動メニュー一覧・検索API
    
    クエリパラメータ:
    - q: キーワード検索（name, descriptionに部分一致）
    - tags: タグ検索（カンマ区切りで複数指定、AND検索）
    - page: ページ番号
    
    並び順:
    - 検索時: 関連度順（nameに一致 > descriptionに一致）
    - 通常時: ID順（登録順）
    
    ページネーション: 5件/ページ、最大20件
    """
    # クエリパラメータを取得
    keyword = request.GET.get('q', '').strip()  # キーワード検索
    tags_param = request.GET.get('tags', '').strip()  # タグ検索（カンマ区切り）
    page_number = request.GET.get('page', 1)
    
    # 基本クエリ（全メニュー）
    exercises = ExerciseMenu.objects.all()
    
    # キーワード検索（OR検索: nameまたはdescriptionに部分一致）
    if keyword:
        exercises = exercises.filter(
            Q(name__icontains=keyword) | 
            Q(description__icontains=keyword) |
            Q(target_area__icontains=keyword)
        )
        
        # 検索時は関連度順にソート（nameに一致が優先、次にdescription）
        # nameに完全一致 > nameに部分一致 > descriptionに一致 の順
        from django.db.models import Case, When, Value, IntegerField
        
        exercises = exercises.annotate(
            relevance=Case(
                When(name__iexact=keyword, then=Value(3)),  # 完全一致（最優先）
                When(name__icontains=keyword, then=Value(2)),  # nameに部分一致
                When(description__icontains=keyword, then=Value(1)),  # descriptionに一致
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-relevance', 'id')
    else:
        # 通常時はID順（登録順）
        exercises = exercises.order_by('id')
    
    # タグ検索（AND検索: 指定された全てのタグを持つメニュー）
    if tags_param:
        tag_names = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
        
        if tag_names:
            # 各タグ名でフィルタリング（AND検索）
            for tag_name in tag_names:
                exercises = exercises.filter(tags__name__icontains=tag_name)
            
            # 重複を除去（ManyToManyで同じメニューが複数回取得される可能性があるため）
            exercises = exercises.distinct()
    
    # ページネーション設定: 1ページあたり5件、最大20件まで表示
    paginator = Paginator(exercises[:20], 5)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        return Response(
            {"error": "指定されたページが存在しません。"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ExerciseMenuSerializer(page_obj, many=True)
    
    return Response({
        "count": paginator.count,  # 総件数
        "total_pages": paginator.num_pages,  # 総ページ数
        "current_page": page_obj.number,  # 現在のページ番号
        "results": serializer.data  # データ
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # ログインユーザーのみアクセス可能
def exercise_detail_view(request, pk: int): # URLから渡される主キー (ID) をpkとして受け取る
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