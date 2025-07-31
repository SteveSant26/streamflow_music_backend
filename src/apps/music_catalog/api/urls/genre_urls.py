from django.urls import path

from ..views.genre_views import get_all_genres, get_genre_detail

urlpatterns = [
    path("", get_all_genres, name="get_all_genres"),
    path("<str:genre_id>/", get_genre_detail, name="get_genre_detail"),
]
