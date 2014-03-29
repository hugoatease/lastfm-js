from flask import Blueprint, current_app, jsonify, redirect, url_for, request
from functools import wraps
from lastfm import LastFM, LastFMError

api = Blueprint('Last.fm API', __name__)

def init_lastfm(session=None):
    public = current_app.config.get('LASTFM_PUBLIC')
    private = current_app.config.get('LASTFM_PRIVATE')
    max_retries = current_app.config.get('LASTFM_MAX_RETRIES')

    return LastFM(public, private, max_retries)

def errorhandler(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            data = function(*args, **kwargs)
            result = {'error': False, 'results': data}
        except LastFMError as error:
            result = {'error': True}
            result.update(error.export())

        return jsonify(result)

    return wrapper

@api.route('/auth')
def auth_init():
    lfm = init_lastfm()
    return redirect(lfm.authURL(url_for('.auth_callback', _external=True)))

@api.route('/callback')
@errorhandler
def auth_callback():
    token = request.args['token']
    lfm = init_lastfm()
    result = lfm.call('auth.getSession', {'token': token})
    return result


@api.route('/<method>/<session>')
@errorhandler
def call(method, session):
    lfm = init_lastfm(session)

    if request.method == 'POST':
        params = request.form
        result = lfm.call(method, params, True)
    else:
        params = request.args
        result = lfm.call(method, params, False)

    return result