from django.conf.urls.defaults import *
from twitterexp.twitterauth.views import callback, unauth, auth

urlpatterns = patterns( 'twitterexp.twitterauth.views',
    #
    # receive OAuth token from twitter
    url( r'^callback$', view=callback, name='oauth_callback' ),
    #
    # logout from the app
    url( r'^logout/$', view=unauth, name='twitter_logout' ),
    #
    # authenticate with twitter using OAuth 
    url( r'^', view=auth, name='oauth_auth' ),
 )
