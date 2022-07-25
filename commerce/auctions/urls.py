from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:url_cat>", views.category, name="category"),
    path("my_history", views.my_history, name="my_history"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("details/<int:primkey>", views.details, name="details")
]
