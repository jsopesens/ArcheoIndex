from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("browse/", views.browse, name="browse"),
    path("page-404/", views.test_404, name="test_404"),
    path("<str:keyword>/", views.single_keyword, name="single_keyword"),
    path("get_children_of/<int:subject_notation>", views.get_children_of, name="getSonsOf"),
    path("getMatchKeywords/<str:search>", views.getMatchKeywords, name="getMatchKeywords"),
]