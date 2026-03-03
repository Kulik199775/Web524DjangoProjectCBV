import random
import string

from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordChangeView, LogoutView
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from users.models import User
from users.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserChangePasswordForm
from users.services import send_register_email, send_new_password

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:user_login')
    template_name = 'users/user_register_update.html'
    extra_context = {
        'title': 'Создать аккаунт',
    }

# def user_register_view(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             new_user = form.save()
#             # print(new_user)
#             # print(form.cleaned_data['password'])
#             new_user.set_password(form.cleaned_data['password']) #хэшируем пароль
#             new_user.save()
#             send_register_email(new_user.email)
#             return HttpResponseRedirect(reverse('users:user_login'))
#     else:
#         form = UserRegisterForm()
#
#     context = {
#         'title': 'Создать аккаунт',
#         'form': form
#     }
#     return render(request, 'users/user_register_update.html', context=context)


def user_login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(email=cd['email'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('dogs:index'))
                return HttpResponse('Аккаунт не активен!')
            return HttpResponse('Нет такого пользователя')
    else:
        form = UserLoginForm()
    context = {
        'title': 'Авторизация',
        'form': form
    }
    return render(request, 'users/user_login.html', context=context)

#если в БД нет значения по умолчанию
# def user_profile_view(request):
#     user_object = request.user
#     if user_object.first_name and user_object.last_name:
#         user_name = user_object.first_name + ' ' + user_object.last_name
#     else:
#         user_name = 'Anonymous'
#     context = {
#         'title': f'Ваш профиль {user_name}'
#     }
#     return render(request, 'users/user_profile_read_only.html', context=context)

@login_required(login_url='users:user_login')
def user_profile_view(request):
    user_object = request.user
    context = {
        'title': f'Ваш профиль {user_object}'
    }
    return render(request, 'users/user_profile_read_only.html', context=context)

@login_required(login_url='users:user_login')
def user_update_view(request):
    user_object = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user_object)
        if form.is_valid():
            user_object = form.save()
            user_object.save()
            return HttpResponseRedirect(reverse('users:user_profile'))
    context = {
        'object': user_object,
        'title': f'Изменить профиль {user_object}',
        'form': UserUpdateForm(instance=user_object)
    }
    return render(request, 'users/user_register_update.html', context=context)

@login_required(login_url='users:user_login')
def user_change_password_view(request):
    user_object = request.user
    form = UserChangePasswordForm(user_object, request.POST)
    if request.method == 'POST':
        if form.is_valid():
            user_object = form.save()
            update_session_auth_hash(request, user_object)
            messages.success(request, 'Пароль был успешно изменён!')
            return HttpResponseRedirect(reverse('users:user_profile'))
        messages.error(request, 'Не удалось изменить пароль!')
    context = {
        'form': form,
        'title':  f'Изменить пароль {user_object}',
    }
    return render(request, 'users/user_change_password.html', context=context)


def user_logout_view(request):
    logout(request)
    return redirect('dogs:index')

@login_required(login_url='users:user_login')
def user_generate_new_password_view(request):
    new_password = ''.join(random.sample(string.ascii_letters + string.digits, k=12))
    request.user.set_password(new_password)
    request.user.save()
    send_new_password(request.user.email, new_password)
    return HttpResponseRedirect(reverse('dogs:index'))
