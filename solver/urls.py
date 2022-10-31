from django.urls import path
from . import views

app_name = "solver"
urlpatterns = [
    path("", views.index, name="index"),
    path("x-sudoku", views.diagonal, name="x-sudoku"),
]