from django.contrib import admin
from django.urls import path , include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from .forms import LoginForm
from . import views as vw 

app_name = "account"

urlpatterns = [
    path('', vw.account , name='account'),
    path('login/', vw.loginView , name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('resetPassword/', auth_views.PasswordResetView.as_view(template_name="account/reset_password.html",success_url='/account/resetPasswordDone/',email_template_name="account/reset_password_email.html"), name='reset_password'),
    path('resetPasswordDone/', auth_views.PasswordResetDoneView.as_view(template_name="account/reset_password_done.html"), name='reset_password_done'),
    path('resetPasswordConfirm/<str:uidb64>/<str:token>/', auth_views.PasswordResetConfirmView.as_view(template_name="account/password_reset_conform.html",success_url='/account/resetPasswordComplete/'), name='reset_password_confirm'),
    path('resetPasswordComplete/', auth_views.PasswordResetCompleteView.as_view(template_name="account/password_reset_complete.html"), name='reset_password_Complete'),
    path('changePassword/', auth_views.PasswordChangeView.as_view(template_name="account/change_password.html",success_url='/account/'), name='change_password'),
]
