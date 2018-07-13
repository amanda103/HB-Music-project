from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from flask_oauthlib.client import OAuth, OAuthException
import os
from flask_debugtoolbar import DebugToolbarExtension
import requests
from pprint import pformat
import json


SPOTIFY_APP_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIFY_APP_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]

eventbrite_token = os.environ["EVENTBRITE_TOKEN"]

eventbrite_url = "https://www.eventbriteapi.com/v3/"


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

    # uncomment this section to test - but wanted to slow down my
    # number of spotify accounts so they don't lock me out!

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    
    # me = spotify.get('v1/me').data
    # user_id = me['id']
    # user_display_name = me['display_name']

    # scope = 'user-top-read'

    # items = spotify.get('v1/me/top/artists').data['items']
    # artists = []
    # for item in items:
    #     artist = item['name']
    #     if artist not in artists:
    #         artists.append(artist)
    # session['users_artists'] = artists
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

    artists =['Angelo De Augustine', 'The Dead Tongues', 'The Stray Birds', 'Shannon Lay', 'Lomelda', 'Anna St. Louis', 'Rhiannon Giddens', 'A. Savage']
    user_id = "21wmm4r33y7chvtoc67kxxouq"
    user_display_name = "Amanda Cantelope"

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

    artists = request.args.getlist('artist')
    # print(artists)
    zipcode = request.args.get('zipcode')
    # print(zipcode)
    distance = request.args.get('distance') + "mi"
    # print(distance)

    requests_list = []

    for artist in artists:
        artist = "+".join(artist.split())
        evt_request = {"method": "GET",
                "relative_url": "events/search/",
                # "token": eventbrite_token,
                # "q": artist,
                # "location.address": zipcode,
                # "location.within": distance,
                # "categories": 103
                "body":"token={}&q={}&location.address={}&location.within={}&categories=103".format(eventbrite_token, artist, zipcode, distance)
        }
        requests_list.append(evt_request)

        # sample requests_list printed to the console:
        
        # [{'method': 'GET', 'relative_url': 'events/search/', 'body': 'token=ZSI3XV6TQYBNNZSEGAUN&q=The+Dead+Tongues&location.address=95060&location.within=25mi&categories=103'}, {'method': 'GET', 'relative_url': 'events/search/', 'body': 'token=ZSI3XV6TQYBNNZSEGAUN&q=Lomelda&location.address=95060&location.within=25mi&categories=103'}, {'method': 'GET', 'relative_url': 'events/search/', 'body': 'token=ZSI3XV6TQYBNNZSEGAUN&q=Rhiannon+Giddens&location.address=95060&location.within=25mi&categories=103'}]


    import pdb; pdb.set_trace()

    headers = {'Authorization': 'Bearer ' + eventbrite_token}

    requests_list_json = jsonify(requests_list)

    response = requests.post(eventbrite_url+"batch/", 
                            headers=headers,
                            data={"batch": requests_list_json})
        # batch response for multiple artists! 

    data = response.json()

    

    return render_template("shows.html", zipcode=zipcode, 
            artists=artists, distance=distance, events=data)





if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)