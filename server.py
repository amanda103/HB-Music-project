from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth, OAuthException
import os
from flask_debugtoolbar import DebugToolbarExtension
import requests
from pprint import pformat

SPOTIFY_APP_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIFY_APP_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]

eventbrite_token = os.environ["EVENTBRITE_TOKEN"]

eventbrite_url = "https://eventbriteapi.com/v3"


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

spotify = oauth.remote_app(
    'spotify',
    consumer_key=SPOTIFY_APP_ID,
    consumer_secret=SPOTIFY_APP_SECRET,
    request_token_params={'scope': 'user-top-read'},
    base_url='https://api.spotify.com/v1',
    request_token_url=None,
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    callback = url_for(
        'spotify_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return spotify.authorize(callback=callback)


@app.route('/login/authorized')
def spotify_authorized():
    # resp = spotify.authorized_response()
    # if resp is None:
    #     return 'Access denied: reason={0} error={1}'.format(
    #         request.args['error_reason'],
    #         request.args['error_description']
    #     )
    # if isinstance(resp, OAuthException):
    #     return 'Access denied: {0}'.format(resp.message)

    # What I need to do is figure out how to get the oauth token from
    # the spotify object - seems like it exists, maybe above method of 
    # .authorized_response() is just not the way to do so. Then I need to 
    # render template and redirect probably to homepage or something with
    # the users top artists - show them their top artists, ask for zipcode
    # and ask how far they're willing to travel!

    resp = spotify.authorized_response()
    if resp is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: {}'.format(resp.message)

    session['oauth_token'] = (resp['access_token'], '')
    access_token = resp['access_token']
    refresh_token = resp['refresh_token']

    return redirect("/account")

@app.route("/account")
def show_acct_info():
    me = spotify.get('v1/me').data
    user_id = me['id']
    user_display_name = me['display_name']

    scope = 'user-top-read'

    items = spotify.get('v1/me/top/artists').data['items']
    artists = []
    for item in items:
        artist = item['name']
        if artist not in artists:
            artists.append(artist)
    session['users_artists'] = artists

    return render_template("hello.html", user_id=user_id, user_display_name=user_display_name, artists=artists)



@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')



@app.route("/logout")
def logout():
    del session['oauth_token']

    return render_template("homepage.html")

@app.route("/search-top-artist-events")
def display_top_artist_events():
    """searches for top artists on eventbrite"""

    query = request.args.get('query')
    location = request.args.get('location')
    distance = request.args.get('distance')
    measurement = "m"


    # If the required information is in the request, look for events
    if location and distance:

        # The Eventbrite API requires the distance value to have a measurement
        distance = distance + measurement

        # TODO: Look for afterparties!

        # - Make a request to the Eventbrite API to search for events that match
        #   the form data.
        # - (Make sure to save the JSON data from the response to the data
        #   variable so that it can display on the page as well.)
        payload ={"token": eventbrite_token, "q": query, 
        "location.address": location, "location.within": distance, 
        "sort_by": sort}


        response = requests.get(eventbrite_url + "events/search", params=payload)
        data = response.json()

        # data = {'This': ['Some', 'mock', 'JSON']}
        events = []

        return render_template("shows.html",
                               data=pformat(data),
                               results=events)

    # If the required info isn't in the request, redirect to the search form
    else:
        flash("Please provide all the required information!")
        return redirect("/afterparty-search")

    return 





if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)