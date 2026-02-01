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
        # 既に登録済みの場合は別のメッセージを返す
        routine, created = Routine.objects.get_or_create(user=request.user, exercise=exercise)
        
        if created:
            return Response(
                {"message": "ルーティンに追加しました"}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": "この運動メニューは既にルーティンに登録されています。"}, 
                status=status.HTTP_200_OK
            )

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