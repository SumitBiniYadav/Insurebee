from django.urls import path
from .views import show_tweets

urlpatterns = [
    path('tweets/', show_tweets, name='show_tweets'),
]
