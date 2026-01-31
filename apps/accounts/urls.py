from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ログインページ
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # ログアウト処理
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'), # ログアウト後にログインページへリダイレクト
    # ユーザー登録ページ
    path('signup/', views.signup_view, name='signup'),
]
