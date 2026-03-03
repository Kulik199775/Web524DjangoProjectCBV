from django.urls import path

from users.apps import UsersConfig
from users.views import (UserRegisterView, UserLoginView, user_profile_view, user_logout_view, user_update_view,
                         user_update_view, user_change_password_view, user_generate_new_password_view)

app_name = UsersConfig.name

urlpatterns = [
    path('', UserLoginView.as_view(), name='user_login'),
    path('logout/', user_logout_view, name='user_logout'),
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('profile/', user_profile_view, name='user_profile'),
    path('update/', user_update_view, name='user_update'),
    path('change_password/',user_change_password_view, name='user_change_password'),
    path('profile/genpassword',user_generate_new_password_view, name='user_generate_password'),

]