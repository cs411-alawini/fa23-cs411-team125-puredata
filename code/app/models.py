# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Playlist(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    created_by_user = models.ForeignKey('User', db_column='created_by_user', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playlist'


class PlaylistSong(models.Model):
    song = models.OneToOneField('Song', on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    inserted_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playlist_song'
        unique_together = (('song', 'playlist'),)


class Recommendation(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    recommended_timsetamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recommendation'
        unique_together = (('user', 'song'),)


class Review(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    content = models.CharField(max_length=1000, blank=True, null=True)
    song_rating = models.IntegerField(blank=True, null=True)
    song_id = models.ForeignKey('Song', blank=True, null=True, on_delete=models.CASCADE)
    user_id = models.ForeignKey('User', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'review'


class ReviewRating(models.Model):
    review_rating = models.IntegerField(blank=True, null=True)
    review = models.OneToOneField(Review, on_delete=models.CASCADE)  # The composite primary key (review_id, user_id) found, that is not supported. The first column is selected.
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'review_rating'
        unique_together = (('review', 'user'),)


class Song(models.Model):
    id = models.CharField(primary_key=True, max_length=22)
    artist = models.CharField(max_length=100, blank=True, null=True)
    album_name = models.CharField(max_length=1000, blank=True, null=True)
    song_name = models.CharField(max_length=1000, blank=True, null=True)
    popularity = models.IntegerField(blank=True, null=True)
    duration_ms = models.IntegerField(blank=True, null=True)
    explicit = models.IntegerField(blank=True, null=True)
    danceability = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    energy = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    key = models.IntegerField(blank=True, null=True)
    loudness = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    mode = models.IntegerField(blank=True, null=True)
    speechiness = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    acousticness = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    instrumentalness = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    liveness = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    valence = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    tempo = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    time_signature = models.IntegerField(blank=True, null=True)
    song_genre = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song'


class SongHistory(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user = models.ForeignKey('User', blank=True, null=True, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, blank=True, null=True, on_delete=models.CASCADE)
    listened_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_history'


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    email = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    password_salt = models.CharField(max_length=32, blank=True, null=True)
    password_hash = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user'
