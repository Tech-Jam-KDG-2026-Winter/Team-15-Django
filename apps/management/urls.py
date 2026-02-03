from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # User
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),

    # Exercise
    path('exercises/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/add/', views.ExerciseCreateView.as_view(), name='exercise_add'),
    path('exercises/<int:pk>/edit/', views.ExerciseUpdateView.as_view(), name='exercise_edit'),
    path('exercises/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise_delete'),

    # Tag
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/add/', views.TagCreateView.as_view(), name='tag_add'),
    path('tags/<int:pk>/edit/', views.TagUpdateView.as_view(), name='tag_edit'),
    path('tags/<int:pk>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
]
