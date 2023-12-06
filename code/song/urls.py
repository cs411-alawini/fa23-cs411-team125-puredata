from django.urls import path
from .views import song_detail, rate_review, delete_rate_review

urlpatterns = [
    path('song/<str:song_id>', song_detail, name='song_detail'),
    path('rate-review/<str:review_id>', rate_review, name='rate_review'),
    path('delete_rate_review/<str:review_id>', delete_rate_review, name='delete_rate_review'),
]