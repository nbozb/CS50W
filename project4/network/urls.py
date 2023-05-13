
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("justChecking", views.justChecking, name="justChecking"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:type>", views.index, name="othindex"),

    #API Routes
    path("posts/<str:type>", views.posts, name="postsbase"),
    path("profiles/<str:profile>", views.profile, name="profiles"),
    path("post/<int:id>", views.post, name="likepost")
]
