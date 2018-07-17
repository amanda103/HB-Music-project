from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from flask_oauthlib.client import OAuth, OAuthException
import os
from flask_debugtoolbar import DebugToolbarExtension
from urllib.parse import urlencode
import requests
from pprint import pformat
import json

# from model import
# remember to source classes from model!

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
    
    me = spotify.get('v1/me').data

    session['user_info'] = {'user_id' : me['id'],
                            'user_display_name' : me['display_name'],
                            'user_followers' : me['followers']['total'],
                            'user_pic_url' : me['images'][0]['url']
                            }


    scope = 'user-top-read'

    items = spotify.get('v1/me/top/artists?time_range=long_term&limit=50&offset=1').data['items']
    artists_info = {}
    artist_ids = []

    for item in items:
        artists_info[item['name']] = {'id': item['id'],
                                    'art_url': item['images'][0]['url'],
                                    'related_artist_info': []
                                    }
        artist_ids.append(item['id'])
        #only getting the first image - is this important? idk
    session['users_artists'] = artists_info
    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

    # dummy data so i'm not pinging spotify every time!

    # artists =['Angelo De Augustine', 'The Dead Tongues', 'The Stray Birds', 'Shannon Lay', 'Lomelda', 'Anna St. Louis', 'Rhiannon Giddens', 'A. Savage']
    # user_id = "21wmm4r33y7chvtoc67kxxouq"
    # user_display_name = "Amanda Cantelope"
    # user_followers = 0
    # user_pic_url = "http://www.dogbazar.org/wp-content/uploads/2014/09/british-bull-dog-puppies.jpg"


    # TABLED FOR NOW - LOOKING AT HOW TO GET RELATED ARTISTS TO DISPLAY MORE SHOWS
    # data = []
    # for item in artist_ids:
    #     url = "https://api.spotify.com/v1/artists/" + item + "/related-artists"
    #     data.append({"method": "GET", "relative_url": url})



    # headers = {'Authorization': 'Bearer ' + session['oauth_token'][0]}

    # response = spotify.get("https://api.spotify.com/v1/artists/" + "batch/", 
    #                         headers=headers,
    #                         data={"batch": json.dumps(data)})
    # import pdb; pdb.set_trace()

    # response = len(response.data)



    return render_template("hello.html",
                            artists_info=artists_info
                            )



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

    artists  = session['users_artists']
    zipcode = request.args.get('zipcode')
    distance = "100mi"

    requests_list = []

    for artist in artists.keys():
        artist = "+".join(artist.split())
        evt_request = {"method": "GET",
                "relative_url": "events/search/",
                "body":"token={}&q={}&location.address={}&location.within={}&categories=103".format(eventbrite_token, artist, zipcode, distance)
        }
        requests_list.append(evt_request)



    headers = {'Authorization': 'Bearer ' + eventbrite_token}


    response = requests.post(eventbrite_url+"batch/", 
                            headers=headers,
                            data={"batch": json.dumps(requests_list)})

    data = response.json()

    # with open('xxx.json', 'w') as outfile:
    #  json.dump(response.json(), outfile, indent=4)

    from process import process_eventbrite_json
    
    shows = process_eventbrite_json(data, artists)

    session['possible_events'] = shows
    

    return render_template("shows.html", data=data, zipcode=zipcode, 
            artists=artists, distance=distance, shows=shows)


@app.route("/account/shows")
def display_user_shows():
    """ shows account page with shows they're going to"""

    shows = request.args.getlist('shows')

    return render_template("hello_shows.html", shows=shows)




if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.debug = True
    # connect_to_db(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)