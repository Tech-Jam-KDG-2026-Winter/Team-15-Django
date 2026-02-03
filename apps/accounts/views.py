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
            messages.success(request, 'アカウントが正常に作成されました。ログインしてください。')
            return redirect('login') # ログインページのURL名
        else:
            pass # テンプレートで form.errors を表示することで対応
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})