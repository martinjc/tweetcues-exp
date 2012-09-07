import datetime
import random
import tweepy

from twitterexp.experiment.user_utils import add_tweet
from twitterexp.experiment.models import ExperimentSetting, Survey, Question, Tweet

def get_settings():
    settings = ExperimentSetting.objects.filter(active=True)
    return random.choice(settings)

def start_survey(user, settings):
    survey, created = Survey.objects.get_or_create(date=datetime.datetime.now(), user=user, settings=settings)
    return survey

def get_questions(api, user, survey, tweets, settings):
    question_types = settings.possible_question_types.all().order_by('?')
    q_no = 1
    questions = []
    for question_set_count in range(3):
        for q_type in question_types:
            question_tweets = []
            tweet = random.choice(tweets)
            question_tweets.append(tweet)
            for i in range(0, settings.num_tweets_displayed - 1):
                unseen_tweet, success = get_random_unseen_tweet(api, tweet)
                while not success:
                    unseen_tweet, success = get_random_unseen_tweet(api, tweet)
                question_tweets.append(unseen_tweet)
            question = Question.objects.create(question_number=q_no, timeline_tweet=tweet, survey=survey, q_type=q_type)
            for question_tweet in question_tweets:
                question.tweets.add(question_tweet)
            if question_tweets >= 2:
                left_tweet_num = random.randint(0,1)
                if left_tweet_num == 0:
                    right_tweet_num = 1
                else:
                    right_tweet_num = 0
                question.left_tweet = question_tweets[left_tweet_num]
                question.right_tweet = question_tweets[right_tweet_num]
            question.save()
            q_no = q_no + 1
            questions.append(question)
    return questions

def get_random_unseen_tweet(api, tweet):
    max = Tweet.objects.count()
    pk = random.randint(0, max)
    try:
        t = Tweet.objects.get(id=pk)
    except Tweet.DoesNotExist:
        return get_random_unseen_tweet(api, tweet)
    if tweet.num_retweets == t.num_retweets:
        return get_random_unseen_tweet(api, tweet)
    elif tweet.author.num_followers == t.author.num_followers:
        return get_random_unseen_tweet(api, tweet)
    elif tweet.author.num_following == t.author.num_following:
        return get_random_unseen_tweet(api, tweet)
    elif tweet.author.num_tweets == t.author.num_tweets:
        return get_random_unseen_tweet(api, tweet)
    try:
        if api.exists_friendship(api.me().id, t.author.twitter_id):
            return get_random_unseen_tweet(api, tweet)
        else:
            return t, True
    except tweepy.TweepError:
        return None, False



