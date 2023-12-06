from django import forms
from app.models import Review, ReviewRating
from django.core.validators import MinValueValidator, MaxValueValidator

class ReviewForm(forms.ModelForm):
    song_rating = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={'min': 0, 'max': 5})
    )
    class Meta:
        model = Review
        fields = ['content', 'song_rating']

class RateReviewForm(forms.ModelForm):
    review_rating = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        widget=forms.NumberInput(attrs={'min': 0, 'max': 5})
    )
    class Meta:
        model = Review
        fields = ['review_rating']