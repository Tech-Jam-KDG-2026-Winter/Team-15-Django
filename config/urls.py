from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from apps.condition_manager.views import exercise_detail_page

from apps.common.api.health import healthz

urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('management/', include('apps.management.urls')),

    path("", TemplateView.as_view(template_name="top.html"), name="top"),
    path("history/", TemplateView.as_view(template_name="history.html"), name="history"),
    path("routines-list/", TemplateView.as_view(template_name="routines.html"), name="routines"),
    path("exercise-list/", TemplateView.as_view(template_name="exercise_list.html"), name="exercise_list"),
    path('exercises/<int:pk>/', exercise_detail_page, name='exercise_detail_page'),

    path("admin/", admin.site.urls),
    path("healthz/", healthz),
    path("api/", include("apps.condition_manager.urls")),
]
