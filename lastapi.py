from flask import Blueprint, jsonify, redirect, url_for, request
import config
from lastfm import LastFM
import json

api = Blueprint('Last.fm API', __name__)

def init_lastfm(session=None):
    return LastFM(config.LASTFM_PUBLIC, config.LASTFM_PRIVATE)

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