from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(SongHistory)
admin.site.register(Song)
admin.site.register(ReviewRating)
admin.site.register(Review)
admin.site.register(Recommendation)
admin.site.register(PlaylistSong)
admin.site.register(Playlist)