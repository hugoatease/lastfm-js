from requests import Session, ConnectionError
from requests.adapters import HTTPAdapter
from hashlib import md5

class LastFMError:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'Last.fm error: ' + self.message

    def export(self):
        return {'reason' : self.message}

class LastFM:
    endpoint = 'http://ws.audioscrobbler.com/2.0/'
    auth_url = 'http://www.last.fm/api/auth/'

    def __init__(self, public_key, secret_key, session=None, max_retries=None):
        self.keys = {'public' : public_key, 'secret' : secret_key}
        self.session = session

        self.request_session = Session()
        if max_retries is not None:
            self.request_session.mount(self.endpoint, HTTPAdapter(max_retries=max_retries))

    def authURL(self, callback):
        url = self.auth_url + '?api_key=' + self.keys['public'] + '&cb=' + callback
        return url

    def queryParams(self, method, params):
        query = {'method': method,
                 'api_key': self.keys['public'],
                 'format': 'json'}
        query.update(params)

        if self.session is not None:
            query['sk'] = self.session

        return query

    def signature(self, query):
        query = query.copy()

        def popIfExists(dict, keys):
            for key in keys:
                if key in dict:
                    dict.pop(key)

        popIfExists(query, ['format', 'callback'])

        result = ''
        for key in sorted(query): #While sorting the keys alphabetically
            #Append each <name><value> pair included in query
            result += key + str(query[key])

        result += self.keys['secret']

        hash = md5(result).hexdigest()
        return hash

    def call(self, method, params, post=False):
        query = self.queryParams(method, params)
        query['api_sig'] = self.signature(query)

        request = self.request_session.request

        try:
            if not post:
                response = request('GET', self.endpoint, params=query)
            else:
                response = request('POST', self.endpoint, data=query)
        except ConnectionError:
            raise LastFMError("Last.fm service is unjoinable. Please try again later.")

        return response.json()