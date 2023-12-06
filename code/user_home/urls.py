from django.urls import path
from .views import home, search_box, add_song_to_playlist, redirect_song, add_song_to_this_playlist, add_playlist, delete_playlist
from song import views

urlpatterns = [
    path('home/', home, name='home'),
    path('search/', search_box,name='search'),
    path('add_playlist/<str:song_id>', add_playlist, name='add_playlist'),
    path('delete_playlist/<str:playlist_id>/<str:song_id>', delete_playlist, name='delete_playlist'),
    path('song/<str:song_id>', views.song_detail, name='song_detail'),
    path('add_song_to_playlist/<str:song_id>', add_song_to_playlist, name='add_song_to_playlist'),
    path('add_song_to_this_playlist/<str:playlist_id>/<str:song_id>', add_song_to_this_playlist,name='add_song_to_this_playlist')
    ]