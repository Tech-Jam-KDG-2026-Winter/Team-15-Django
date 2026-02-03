from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView # トップページと履歴ページを表示するために追加

# from django.http import JsonResponse # root関数が不要になるため削除
from apps.common.api.health import healthz # これは残します

# def root(request): # root関数が不要になるため削除
#     return JsonResponse({"service": "django-starter", "status": "ok"})

urlpatterns = [
    # accountsアプリのURLをインクルード (認証関連)
    path('accounts/', include('apps.accounts.urls')),
    # managementアプリのURLをインクルード (管理画面関連)
    path('management/', include('apps.management.urls')),

    # トップページ (今回は認証機能のみなので、一時的にデフォルトのルートパスを変更)
    path("", TemplateView.as_view(template_name="top.html"), name="top"),
    # ▼ UI確認用（仮）
    path("history/", TemplateView.as_view(template_name="history.html"), name="history"),
    path("routines-list/", TemplateView.as_view(template_name="routines.html"), name="routines"),
    path("exercise-list/", TemplateView.as_view(template_name="exercise_list.html"), name="exercise_list"),

    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    path("api/", include("apps.condition_manager.urls")), # APIのURLはそのまま
]
