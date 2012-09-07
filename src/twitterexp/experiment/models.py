from django.db import models
from django.contrib.auth.models import User

class QuestionType( models.Model ):
    INFO_SEEN = (
        ( 'A', 'Tweet Text' ),
        ( 'B', 'Screen Name' ),
        ( 'C', 'Name' ),
        ( 'D', 'Avatar' ),
        ( 'E', 'Friendship' ),
        ( 'F', 'Follower Count' ),
        ( 'G', 'Following Count' ),
        ( 'H', 'Tweet Count' ),
        ( 'I', 'Number of Retweets' ),
        ( 'J', 'Date' ),
        ( 'K', 'Screen Name and Avatar' ),
        ( 'L', 'Screen Name and Follower Count' ),
        ( 'M', 'Screen Name and Following Count' ),
        ( 'N', 'Screen Name and Tweet Count' ),
        ( 'O', 'Screen Name and Number of Retweets' ),
        ( 'P', 'Avatar and Follower Count' ),
        ( 'Q', 'Avatar and Following Count' ),
        ( 'R', 'Avatar and Tweet Count' ),
        ( 'S', 'Avatar and Number of Retweets' ),
        ( 'T', 'Friendship and Follower Count' ),
        ( 'U', 'Friendship and Following Count' ),
        ( 'V', 'Friendship and Tweet Count' ),
        ( 'W', 'Friendship and Number of Retweets' ),
        ( 'X', 'Screen Name, Avatar, Name and Follower Count' ),
        ( 'Y', 'Screen Name, Avatar, Name and Following Count' ),
        ( 'Z', 'Screen Name, Avatar, Name and Tweet Count' ),
        ( '1', 'Screen Name, Avatar, Name and Number of Retweets' ),

    )
    q_type = models.CharField( max_length=1, choices=INFO_SEEN )
    tweet_text = models.BooleanField()
    screen_name = models.BooleanField()
    name = models.BooleanField()
    avatar = models.BooleanField()
    friendship = models.BooleanField()
    follower_count = models.BooleanField()
    following_count = models.BooleanField()
    tweet_count = models.BooleanField()
    num_retweets = models.BooleanField()
    date = models.BooleanField()

    def __unicode__( self ):
        return self.get_q_type_display()

class ExperimentSetting( models.Model ):
    name = models.CharField( max_length=140 )
    required_num_followers = models.IntegerField( 'Required Number of Followers' )
    required_num_following = models.IntegerField( 'Required Number Following' )
    num_tweets_displayed = models.IntegerField( 'Number of Tweets Displayed' )
    possible_question_types = models.ManyToManyField( QuestionType )
    num_questions = models.IntegerField( 'Number of Questions' )
    active = models.BooleanField()

    def q_types( self ):
        return ', '.join( [q.get_q_type_display() for q in self.possible_question_types.all()] )

# Twitter User
class TwitterUser( models.Model ):
    twitter_id = models.BigIntegerField( primary_key=True )
    name = models.CharField( max_length=100, blank=True, null=True )
    screen_name = models.CharField( max_length=100 )
    profile_image_url = models.URLField()
    num_followers = models.IntegerField( blank=True, null=True )
    num_following = models.IntegerField( blank=True, null=True )
    num_tweets = models.IntegerField( blank=True, null=True )

# Create your models here.
class ExperimentUser( models.Model ):
    user = models.OneToOneField( User, unique=True, related_name='surveys' )
    twitter_user = models.ForeignKey( TwitterUser, related_name='+' )
    contactable = models.BooleanField()
    confirmation_code = models.CharField(max_length=100, blank=True, null=True)
    email_address = models.CharField( max_length=200, blank=True, null=True )
    started = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)

# A Tweet
class Tweet( models.Model ):
    tweet_id = models.BigIntegerField( unique=True )
    author = models.ForeignKey( TwitterUser, related_name='statuses' )
    text = models.CharField( 'content', max_length=160 )
    created_at = models.DateTimeField( blank=True )
    num_retweets = models.IntegerField( 'retweets' )
    html_embed = models.TextField( blank=True, null=True )

# A Survey
class Survey( models.Model ):
    date = models.DateTimeField( blank=True )
    user = models.ForeignKey( ExperimentUser, related_name='surveys' )
    settings = models.ForeignKey( ExperimentSetting, related_name='surveys' )

# A Question
class Question( models.Model ):
    question_number = models.IntegerField()
    timeline_tweet = models.ForeignKey( Tweet, related_name='timeline_in' )
    selected_tweet = models.ForeignKey( Tweet, related_name='chosen_in', blank=True, null=True )
    tweets = models.ManyToManyField( Tweet )
    survey = models.ForeignKey( Survey, related_name='responses' )
    q_type = models.ForeignKey( QuestionType, related_name='questions' )
    left_tweet = models.ForeignKey(Tweet, related_name='left_tweet_in', blank=True, null=True)
    right_tweet = models.ForeignKey(Tweet, related_name='right_tweet_in', blank=True, null=True)

    def followers_larger( self ):
        if self.selected_tweet is None:
            return False
        for tweet in self.tweets.all():
            if tweet.tweet_id != self.selected_tweet.tweet_id and tweet.author.num_followers > self.selected_tweet.author.num_followers:
                return False
        return True

    def following_larger( self ):
        if self.selected_tweet is None:
            return False
        for tweet in self.tweets.all():
            if tweet.tweet_id != self.selected_tweet.tweet_id and tweet.author.num_following > self.selected_tweet.author.num_following:
                return False
        return True

    def tweets_larger( self ):
        if self.selected_tweet is None:
            return False
        for tweet in self.tweets.all():
            if tweet.tweet_id != self.selected_tweet.tweet_id and tweet.author.num_tweets > self.selected_tweet.author.num_tweets:
                return False
        return True

    def retweets_larger( self ):
        if self.selected_tweet is None:
            return False
        for tweet in self.tweets.all():
            if tweet.tweet_id != self.selected_tweet.tweet_id and tweet.num_retweets > self.selected_tweet.num_retweets:
                return False
        return True
