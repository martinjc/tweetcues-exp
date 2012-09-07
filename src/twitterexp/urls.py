from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns( '',
    #
    # root urls used for experiment
    url( r'^', include( 'twitterexp.experiment.urls' ) ),

    #
    # auth urls used for auth application
    url( r'^auth/', include( 'twitterexp.twitterauth.urls' ) ),


    url( r'^admin/', include( admin.site.urls ) ),
 )
