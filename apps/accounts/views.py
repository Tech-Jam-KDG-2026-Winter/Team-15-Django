from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm # 作成したフォームをインポート

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