from requests import request
from hashlib import md5


class LastFM:
    endpoint = 'http://ws.audioscrobbler.com/2.0/'
    auth_url = 'http://www.last.fm/api/auth/'

    def __init__(self, public_key, secret_key, session=None):
        self.keys = {'public' : public_key, 'secret' : secret_key}
        self.session = session

    def authURL(self):
        url = self.auth_url + '?api_key=' + self.keys['public']
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

        if not post:
            response = request('GET', self.endpoint, params=query)
        else:
            response = request('POST', self.endpoint, data=query)

        return response.content