from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:keyword>/", views.single_keyword, name="single_keyword"),
    path("get_children_of/<int:subject_notation>", views.get_children_of, name="getSonsOf"),
    path("getMatchKeywords/<str:search>", views.getMatchKeywords, name="getMatchKeywords"),
]