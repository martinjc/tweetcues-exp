from django.http import *
from django.conf import settings
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, check_password
from django.contrib.auth.decorators import login_required

from tweepy import API, OAuthHandler, TweepError

from twitterexp.experiment.user_utils import get_or_add_user, add_or_update_twitter_user

CONSUMER_KEY = getattr(settings, 'CONSUMER_KEY_TWITTER_EXP', '')
CONSUMER_SECRET = getattr(settings, 'CONSUMER_SECRET_TWITTER_EXP', '')
ROOT_URL = getattr(settings, 'ROOT_URL', '')

def get_api(request):
    """
    set up and return a Twitter api object
    """
    oauth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    access_key = request.session['access_key_twitterexp']
    access_secret = request.session['access_secret_twitterexp']
    oauth.set_access_token(access_key, access_secret)
    api = API(oauth)
    return api

def check_key(request):
    """
    Check to see if we already have an access_key stored
    """
    try:
        access_key = request.session.get('access_key_twitterexp', None)
        if not access_key:
            return False
    except KeyError:
        return False
    return True

def unauth(request):
    if check_key(request):
        request.session.clear()
        logout(request)
    return HttpResponseRedirect(reverse('experiment_main'))

def auth(request):
    """
    Perform authentication with Twitter
    """
    # start the OAuth process, set up a handler with our details
    oauth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    # direct the user to the authentication url
    auth_url = oauth.get_authorization_url()
    response = HttpResponseRedirect(auth_url)
    # store the request token
    request.session['unauthed_token_twitterexp'] = (oauth.request_token.key, oauth.request_token.secret)
    return response

def callback(request):
    """
    Receive the Oauth token back from Twitter
    """
    verifier = request.GET.get('oauth_verifier')
    if verifier is None:
        response = HttpResponseRedirect(reverse('experiment_main'))
        return response
    oauth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    token = request.session.get('unauthed_token_twitterexp', None)
    if token is None:
        request.session['auth_error'] = True
        return HttpResponseRedirect(ROOT_URL)

    request.session['auth_error'] = False
    # remove the request token now we don't need it
    request.session.delete('unauthed_token_twitterexp')
    oauth.set_request_token(token[0], token[1])
    # get the access token and store
    try:
        oauth.get_access_token(verifier)
    except TweepError:
        print 'Error, failed to get access token'
        request.session['auth_error'] = True
        return HttpResponseRedirect(ROOT_URL)
    request.session['access_key_twitterexp'] = oauth.access_token.key
    request.session['access_secret_twitterexp'] = oauth.access_token.secret

    api = get_api(request)
    twitter_user = api.me()

    twitter_user = add_or_update_twitter_user(twitter_user)

    experiment_user, user = get_or_add_user(twitter_user)

    user.set_password('')

    user = authenticate(username=twitter_user.twitter_id, password='')
    login(request, user)

    response = HttpResponseRedirect(reverse('experiment_start'))
    return response
