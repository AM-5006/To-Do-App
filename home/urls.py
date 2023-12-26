from django.urls import path,include
from django.contrib.auth.views import LoginView

from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("profile_page/", profile, name="profile_page"),
    path("signup/", signup, name="signup"),
    path('signin/', LoginView.as_view(template_name='login.html'), name='signin'),
    path('logout/', logout_view, name='logout'),
    # path("signin/", signin, name="signin"),

    path('confirmation/', confirmation_page_view, name='confirmation_page'),

    path("activation-expired", activation_expired, name="activation-expired"),
    path("invalid-token", invalid_token, name="invalid-token"),
]
