from django.contrib.auth.models import User
from twitterexp.experiment.models import TwitterUser, ExperimentUser, Tweet
import tweepy
import random


def get_or_add_user(twitter_user):
    try:
        user = User.objects.get(username=twitter_user.twitter_id)
    except User.DoesNotExist:
        user = User.objects.create_user(username=twitter_user.twitter_id, email='', password='')
    experiment_user, created = ExperimentUser.objects.get_or_create(user=user, twitter_user=twitter_user)
    return experiment_user, user

def add_or_update_twitter_user(twitter_user):
    t_u, created = TwitterUser.objects.get_or_create(twitter_id=twitter_user.id, defaults={'screen_name' : twitter_user.screen_name,
                                                                                            'profile_image_url' : twitter_user.profile_image_url,
                                                                                            'name' : twitter_user.name})
    if twitter_user.followers_count:
        t_u.num_followers = twitter_user.followers_count
    if twitter_user.friends_count:
        t_u.num_following = twitter_user.friends_count
    if twitter_user.statuses_count:
        t_u.num_tweets = twitter_user.statuses_count

    t_u.save()
    return t_u

def get_user_tweets(api, num):
    """
    get a number of tweets from a user's timeline
    """
    tweets = []
    for t in tweepy.Cursor(api.home_timeline).items(num):
        tweets.append(add_tweet(t))
    return tweets

def add_tweet(tweet):
    author = add_or_update_twitter_user(tweet.author)
    t, created = Tweet.objects.get_or_create(tweet_id=tweet.id, defaults={'author' : author,
                                                                            'text' : tweet.text,
                                                                            'created_at' : tweet.created_at})
    num_retweets = tweet.retweet_count
    if type(num_retweets) == type(''):
        num_retweets = num_retweets[0:-1]
    t.num_retweets = num_retweets
    t.save()
    return t
