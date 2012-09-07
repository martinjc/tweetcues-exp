import copy
import httplib
import urllib
import urllib2
import json

class TwitterAPI:

    def __init__(self, api):

        self.api = api

        self.scheme = 'https://'
        self.root = 'api.twitter.com'
        self.version = '/1'

        self.api_base_url = self.scheme + self.root + self.version

    def query(self, path, get_params):
        params = copy.copy(get_params)

        path = path.lstrip('/')

        url = self.api_base_url + '/' + path + '?' + urllib.urlencode(params)

        self.headers = {}

        self.api.auth.apply_auth(url, 'GET', self.headers, params)

        conn = httplib.HTTPSConnection(self.root)

        try:
            conn.request('GET', url, headers=self.headers)
            resp = conn.getresponse()
        except urllib2.HTTPError, e:
            raise e
        except urllib2.URLError, e:
            raise e
        except Exception, e:
            raise e

        if resp.status != 200:
            return '', False

        data = resp.read()

        conn.close()

        return data, True

    def get_tweet_embed_code(self, tweet_id):
        endpoint = 'statuses/oembed.json'
        params = {'id' : tweet_id, 'align' : 'center', 'omit_script' : True, 'hide_thread' : True, 'hide_media' : True, 'related' : 'martinjc,recognitionEU'}
        data, success = self.query(endpoint, params)
        if success:
            html = json.loads(data)['html']
            return html, success
        else:
            return data, success
