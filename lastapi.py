from flask import Blueprint, current_app, jsonify, redirect, url_for, request
from lastfm import LastFM

api = Blueprint('Last.fm API', __name__)

def init_lastfm(session=None):
    public = current_app.config.get('LASTFM_PUBLIC')
    private = current_app.config.get('LASTFM_PRIVATE')
    return LastFM(public, private)

@api.route('/auth')
def auth_init():
    lfm = init_lastfm()
    return redirect(lfm.authURL(url_for('.auth_callback', _external=True)))

@api.route('/callback')
def auth_callback():
    token = request.args['token']
    lfm = init_lastfm()
    result = lfm.call('auth.getSession', {'token': token})
    return jsonify(result)


@api.route('/<method>/<session>')
def call(method, session):
    lfm = init_lastfm(session)

    if request.method == 'POST':
        params = request.form
        result = lfm.call(method, params, True)
    else:
        params = request.args
        result = lfm.call(method, params, False)

    return jsonify(result)