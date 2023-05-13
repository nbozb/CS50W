from django.urls import path
from . import views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("random", views.random, name="random"),
    path("search", views.search, name="search"),
    path("newpage", views.newpage, name="newpage"),
    path("<str:title>/edit", views.editpage, name="editpage"),
    path("<str:title>", views.entry, name="entry")
]
