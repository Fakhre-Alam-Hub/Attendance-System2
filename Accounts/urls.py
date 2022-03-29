from django.urls import path
from Accounts import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='account_register'),
    path('login/', auth_views.LoginView.as_view(template_name='Accounts/login.html'), name='account_login'),
    path('profile/', views.profile, name='account_profile'),
    path('logout/', auth_views.LogoutView.as_view(template_name='Accounts/logout.html'), name='account_logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='Accounts/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='Accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='Accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
