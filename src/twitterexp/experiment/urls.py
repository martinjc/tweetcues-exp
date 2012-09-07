from django.conf.urls.defaults import *
from twitterexp.experiment.views import main, start, get_tweets, question, answer, done, restart, get_tweet_embed_html, check_rate_limit_status, validate

urlpatterns = patterns('experiment.views',
    #
    # main page, login etc
    url(r'^$', view=main, name='experiment_main'),
    #
    # attempt to start the experiment
    url(r'^start/$', view=start, name='experiment_start'),

    #
    # background url to start the process of retrieving tweets for the experiment
    url(r'^get_tweets/$', view=get_tweets, name='experiment_get_tweets'),

    #
    #
    url(r'^question/$', view=question, name='experiment_question'),

    #
    #
    url(r'^answer/$', view=answer, name='experiment_answer'),

    #
    #
    url(r'^done/$', view=done, name='experiment_done'),

    #
    #
    url(r'^restart/$', view=restart, name='experiment_restart'),

    #
    #
    url(r'^tweet_embed/(?P<tweet_id>\w+)/$', view=get_tweet_embed_html, name='experiment_tweet_embed'),

    #
    #
    url(r'^rate_limit/$', view=check_rate_limit_status, name='experiment_rate'),

    #
    #
    url(r'^validate/$', view=validate, name='validate'),
 )
