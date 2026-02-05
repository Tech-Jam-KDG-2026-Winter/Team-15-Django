from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm # 作成したフォームをインポート
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        # nextパラメータがある場合はそれを優先
        url = self.get_redirect_url()
        if url:
            return url
        
        # スタッフ権限がある場合は管理者ダッシュボードへ
        if self.request.user.is_staff:
            return reverse_lazy('management:dashboard')
        
        # それ以外はデフォルトの設定(LOGIN_REDIRECT_URL)に従う
        return super().get_success_url()

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ユーザー登録後、自動的にログイン
            messages.success(request, '登録が完了し、自動的にログインしました。')
            return redirect('top')  # トップページのURL名
        else:
            # フォームが無効な場合は、エラーメッセージと共に再度フォームを表示
            # messages.error(request, '入力内容に誤りがあります。') # 必要に応じて
            pass
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})