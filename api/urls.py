from django.urls import path,include
from django.contrib.auth import views as auth_views

from .views import Register, VerifyEmail, Login, GenerateActivationLinkView, Profile, TaskView

urlpatterns = [
    #User
    path('register/', Register.as_view(), name="register"),
    path('login/', Login.as_view(), name="login"),
    path('profile/', Profile.as_view(), name="profile"),
    path('update-profile/',Profile.as_view(),name="update_profile"),
    
    #Task
    path('task/', TaskView.as_view(), name="task"),
    path('task-modify/<int:pk>/', TaskView.as_view(), name='task-modify'),

    #User verification
    path('email-verify/',VerifyEmail.as_view(),name="email-verify"),
    path('generate-activation-link/', GenerateActivationLinkView.as_view(), name="generate-activation-link"),

    #Forgot Password
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
]