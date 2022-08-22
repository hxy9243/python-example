import os

import flask
from flask import Flask
import requests
from jinja2 import Environment, PackageLoader, select_autoescape
import google_auth_oauthlib.flow


CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
]
app = Flask(__name__)
app.secret_key = 'SOME SECRET HERE'

SCHEME = 'https'

if os.environ.get('DEBUG', None):
    SCHEME = 'http'

env = Environment(
    loader=PackageLoader('app'),
    autoescape=select_autoescape(),
)


@app.route('/')
def landing():
    index = env.get_template('index.jinja')

    return index.render()


@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES,
    )
    flow.redirect_uri = flask.url_for(
        'oauth2callback', _external=True, _scheme=SCHEME)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_grant_scopes='true',
    )
    flask.session['state'] = state
    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state,
    )
    flow.redirect_uri = flask.url_for(
        'oauth2callback', _external=True, _scheme=SCHEME)

    flask.request.scheme = SCHEME
    authorization_response = flask.request.url

    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        return 'Error: getting auth token from OAuth server: {}'.format(e)

    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for('info'))


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }


@app.route('/resources/info')
def info():
    if 'credentials' not in flask.session:
        return flask.redirect('/authorize')

    credentials = flask.session['credentials']

    print('header', {'Authorization': 'Bearer ' + credentials['token']})
    resp = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': 'Bearer ' + credentials['token']})

    if resp.status_code == 401:
        return flask.redirect('/authorize')

    print('response: ', resp.json())

    infopage = env.get_template('info.jinja')
    return infopage.render(**resp.json())


if __name__ == '__main__':
    app.run()
