from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


@require_POST
def check_user(request):
    username = request.POST.get('username')
    if not username:
        return HttpResponse("")

    # Теперь это сработает для твоей модели 'user.User'
    exists = User.objects.filter(username=username).exists()
    color = "var(--green)" if exists else "var(--red)"
    icon = "✔" if exists else "✘"
    return HttpResponse(f'<span style="color: {color};">{icon}</span>')


@require_POST
def login_view(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user:
        login(request, user)
        # Возвращаем HTML только для блока авторизации
        return HttpResponse(f'''
            <div class="auth-form" hx-swap-oob="true" id="auth-section">
                <span style="font-family: var(--mono); font-size: 13px; color: var(--muted);">
                    <span style="color: var(--green);">●</span> {user.username}
                </span>
                <button class="btn btn-outline" 
                        hx-post="/auth/logout/" 
                        hx-target="#auth-section" 
                        style="padding: 4px 10px; font-size: 11px;">
                    Выйти
                </button>
                <script>showToast("Вы вошли как {user.username}", "success");</script>
            </div>
        ''')

    # Если пароль неверный, возвращаем ошибку в статус
    return HttpResponse('<span style="color: var(--red);">Неверный пароль</span>',
                        status=200)


@require_POST
def logout_view(request):
    logout(request)
    # Возвращаем пустую форму входа (лучше вынести в отдельный шаблон header_auth.html)
    return render(request, 'includes/header_auth_form.html')
