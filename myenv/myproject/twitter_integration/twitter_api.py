from django.shortcuts import render
import requests
from django.core.cache import cache
from django.conf import settings

BEARER_TOKEN = settings.TWITTER_BEARER_TOKEN
USERNAME = 'brijbinisy'

def get_user_id(username): 
    cached_user_id = cache.get("twitter_user_id")
    if cached_user_id:
        return cached_user_id

    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"} 
    response = requests.get(url, headers=headers)
    if response.status_code != 200: 
        raise Exception(f"Cannot fetch user ID: {response.text}")
    
    user_id = response.json()['data']['id']
    cache.set("twitter_user_id", user_id, timeout=60 * 60)  # Cache for 1 hour
    return user_id

def get_recent_tweets(user_id, max_results=5):
    cached_tweets = cache.get("recent_tweets")
    if cached_tweets:
        return cached_tweets

    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    params = {"max_results": max_results}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Cannot fetch tweets: {response.text}")
    
    tweets = response.json().get('data', [])
    cache.set("recent_tweets", tweets, timeout=60 * 5)  # Cache tweets for 5 mins
    return tweets

def tweets_view(request):
    try:
        user_id = get_user_id(USERNAME)
        tweets = get_recent_tweets(user_id)
        return render(request, "tweets.html", {"tweets": tweets})
    except Exception as e:
        return render(request, "tweets.html", {"error": str(e)})
