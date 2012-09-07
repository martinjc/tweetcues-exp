# Create your views here.
import random
import uuid
import json
import datetime

from django.http import *
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from twitterexp.twitterauth.views import check_key, get_api
from twitterexp.experiment.experiment_utils import get_settings, start_survey, get_questions
from twitterexp.experiment.user_utils import get_user_tweets
from twitterexp.experiment.models import Survey, ExperimentSetting, Tweet, ExperimentUser
from twitterexp.experiment.tweet_api import TwitterAPI
ROOT_URL = getattr(settings, 'ROOT_URL', '')



def main(request):
    """
    Main Page - if we are already authenticated go to the info page ready to start the questions.
    Otherwise, show the login page.
    """
    auth_error = request.session.get('auth_error', False)
    if auth_error:
        request.session.clear()
        logout( request )
    exp_settings = get_settings()
    request.session['settings_id'] = exp_settings.id
    return render_to_response( 'main.html', {'followers' : exp_settings.required_num_followers, 'following' : exp_settings.required_num_following, 'root_url' : ROOT_URL, 'auth_error' : auth_error} )


@login_required
def start(request):
    """
    Make sure we are ready to start the survey
    """
    if check_key(request):
        api = get_api(request)
        user = api.me()

        # get the currently active settings and the user profile
        exp_settings = ExperimentSetting.objects.get(id=request.session['settings_id'])
        exp_user = request.user.get_profile()

        # make sure user meets the requirements for the experiment
        if user.friends_count >= exp_settings.required_num_following and user.followers_count >= exp_settings.required_num_following:

            survey = start_survey(exp_user, exp_settings)
            request.session['survey_id'] = survey.id

            return render_to_response('start.html', {'user' : exp_user, 'root_url' : ROOT_URL}, context_instance=RequestContext(request))

        else:

            request.user.delete()
            exp_user.delete()

            return render_to_response('fail.html', {'user' : user, 'root_url' : ROOT_URL})
    else:
        request.session.clear()
        logout(request)
        return render_to_response('fail.html', {'auth_error' : True, 'root_url' : ROOT_URL})


@login_required
def get_tweets(request):
    api = get_api(request)
    user = api.me()

    survey_id = request.session.get('survey_id', None)
    survey = Survey.objects.get(id=survey_id)

    tweets = get_user_tweets(api, 120)

    exp_settings = ExperimentSetting.objects.get(id=request.session['settings_id'])

    questions = get_questions(api, user, survey, tweets, exp_settings)

    return  HttpResponse('<p>Ok, we\'re all set. Click the "Start The Quiz" button when you are ready to begin.</p>', mimetype="text/html")


@login_required
def question(request):

    number = request.session.get('question_number')
    if number:
        survey_id = request.session.get('survey_id', None)
        survey = Survey.objects.get(id=survey_id)
        question = survey.responses.get(question_number=number)
        if not question.selected_tweet is None:
            number += 1
    else:
        number = 1
        exp_user = request.user.get_profile()
        exp_user.started = datetime.datetime.today()
        exp_user.save()

    request.session['question_number'] = number

    survey_id = request.session.get('survey_id', None)
    survey = Survey.objects.get(id=survey_id)

    exp_settings = ExperimentSetting.objects.get(id=request.session['settings_id'])

    if number <= exp_settings.num_questions:
        question = survey.responses.get(question_number=number)
        q_tweets = question.tweets.all().order_by('?')
        return render_to_response('question.html', {'question' : question, 'tweets': q_tweets, 'settings' : exp_settings, 'root_url' : ROOT_URL, 'user' : request.user.get_profile()}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('experiment_done'))

@login_required
def answer(request):

    # get the answer (the id of the tweet that was selected)
    answer = request.POST.get('answer')
    if answer is None:
        return HttpResponseRedirect(reverse('experiment_question'))

    # get the current response id
    question_id = request.POST.get('question_id')

    if question_id is None:
        return HttpResponseRedirect(reverse('experiment_question'))

    survey_id = request.session.get('survey_id', None)
    survey = Survey.objects.get(id=survey_id)

    q = survey.responses.get(id=question_id)
    tweet = q.tweets.get(tweet_id=answer)

    q.selected_tweet = tweet
    q.save()
    survey.save()

    if len(survey.responses.filter(selected_tweet=None).all()) > 0:
        return HttpResponseRedirect(reverse('experiment_question'))
    else:
        return HttpResponseRedirect(reverse('experiment_done'))


@login_required
def done(request):
    uid = uuid.uuid4()
    user = request.user.get_profile()
    user.confirmation_code = uid
    user.finished = datetime.datetime.today()
    user.save()
    request.session.clear()
    return render_to_response('done.html', {'user' : user, 'confirmation_code' : uid, 'root_url' : ROOT_URL})


@login_required
def restart(request):
    request.session['question_number'] = 1
    exp_settings = get_settings()
    request.session['settings_id'] = exp_settings.id
    return HttpResponseRedirect(reverse('experiment_start'))


@login_required
def get_tweet_embed_html(request, tweet_id):
    try:
        tweet = Tweet.objects.get(tweet_id=tweet_id);
    except Tweet.DoesNotExist:
        return HttpResponse('<div class="alert-message warning"><p>Error retrieving tweet from database, this is not good!</p></div>')

    html = tweet.html_embed
    if html == '' or html is None:
        api = get_api(request)
        tapi = TwitterAPI(api)
        html, success = tapi.get_tweet_embed_code(tweet.tweet_id)
        if success:
            tweet.html_embed = html
            tweet.save()
        else:
            html = '<div class="alert-message warning"><p>Error retrieving tweet from twitter (might have been deleted?)</p></div>'

    return HttpResponse(html, mimetype='text/html')


def validate(request):
    confirmation_code = request.GET.get('confirmation_code', None)
    if confirmation_code is not None:
        if confirmation_code == "" or len(confirmation_code) < 2:
            return return_data(request, {'verified': False, 'confirmation_code': confirmation_code})
    else:
        return return_data(request, {'verified': False, 'confirmation_code': confirmation_code})
    experiment_users = ExperimentUser.objects.all()
    confirmation_codes = []
    for user in experiment_users:
        confirmation_codes.append(user.confirmation_code)

    if confirmation_code in confirmation_codes:
        return return_data(request, {'verified': True, 'confirmation_code': confirmation_code})
    else:
        return return_data(request, {'verified': False, 'confirmation_code': confirmation_code})


@login_required
def check_rate_limit_status(request):
    api = get_api(request)
    data = api.rate_limit_status()
    remaining = data['remaining_hits']
    if remaining < 10:
        message = "<div class='alert-message warning'><p>Looks like we're out of twitter juice, that'll have to do for now!</p></div>"
        return render_to_response('done.html', {'user' : request.user.get_profile(), 'root_url' : ROOT_URL, 'message': message })


def return_data(request, data_dict):
    """
    Return json data in the correct format dependent on whether this is a json or jsonp request
    """

    callback = request.GET.get('callback', None)

    if callback is None:
        return HttpResponse(json.dumps( data_dict ), mimetype = 'application/json')
    else:
        return HttpResponse(callback + '(' + json.dumps( data_dict ) + ')', mimetype = 'application/javascript')

