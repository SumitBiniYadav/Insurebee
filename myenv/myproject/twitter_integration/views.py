from django.shortcuts import render
from .twitter_api import get_user_id, get_recent_tweets

USERNAME = 'brijbinisy'

def show_tweets(request):
    try:
        user_id = get_user_id(USERNAME)
        tweets = get_recent_tweets(user_id)
        return render(request, 'tweets.html', {'tweets': tweets})
    except Exception as e:
        return render(request, 'tweets.html', {'error': str(e)})
