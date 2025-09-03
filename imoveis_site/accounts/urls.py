from django.urls import path # type: ignore
from django.contrib.auth import views as auth_view
from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login/", views.login_view, name="login"),
    
]
