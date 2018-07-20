from flask import Flask, redirect, url_for, session, request, render_template, jsonify, flash
from flask_oauthlib.client import OAuth, OAuthException
import os
from flask_debugtoolbar import DebugToolbarExtension
from urllib.parse import urlencode
import requests
from pprint import pformat
import json

from datetime import datetime

from model import User, Artist, Event, UsersEvents, UsersArtists, ArtistsEvents, db, connect_to_db

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

@app.before_request
def before_request():
    if 'user_info' not in session and request.endpoint not in ['login', 'spotify_authorized', 'show_acct_info']:
        return redirect(url_for('login'))

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

    me = spotify.get('v1/me').data

    user_id = me['id']

    session['user_info'] = {'user_id' : me['id'],
                            'user_display_name' : me['display_name'],
                            'user_followers' : me['followers']['total'],
                            'user_pic_url' : me['images'][0]['url']
                            }

    is_user_there = db.session.query(User).filter(User.spotify_user_id == user_id).first()

    if is_user_there:
        flash("WELCOME BACK")
    else:
        new_user = User(spotify_user_id=me['id'], pic_url=me['images'][0]['url'], display_name=me['display_name'])
        db.session.add(new_user)
        db.session.commit()

    scope = 'user-top-read'

    items = spotify.get('v1/me/top/artists?time_range=long_term&limit=50&offset=1').data['items']
    artists_info = {}
    # artist_ids = []

    for item in items:
        artists_info[item['name']] = {'id': item['id'],
                                    'art_url': item['images'][0]['url'],
                                    'related_artist_info': []
                                    }
        # artist_ids.append(item['id'])
        #only getting the first image - is this important? idk

    # Maybe I would make an instance of the Artist class here so that I could query the 
    # database on the next go round - seems hard to pass all this info through session/jinja/jquery

   

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
                            artists_info=artists_info,
                            )



@spotify.tokengetter
def get_spotify_oauth_token():
    return session.get('oauth_token')


@app.route("/logout")
def logout():
    del session['oauth_token']
    flash("Logout successful")

    return render_template("homepage.html")


@app.route("/search-top-artist-events")
def display_top_artist_events():
    """searches for top artists on eventbrite"""

    # having trouble deciding how to grab each artist on by one bc the number of artists/inputs
    # generated depends on the spotify data.
    # maybe put artists in db on first go round! Keep track of artists??

    # artists  = { "artist_name" : request.args.get("")

    #             }



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

    from process import process_eventbrite_json
    
    shows = process_eventbrite_json(data, artists)
    # EXAMPLE DATA --> this is what one show will look like in dict of shows
    # {'48141455389': {'event_id': '48141455389',
    # 'venue_id': '24141496', 
    # 'logo': {'url': 'https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F47272144%2F188968768274%2F1%2Foriginal.jpg?auto=compress&s=885b31c9ed54c4e143a61547fc9f583b', 'width': 960, 'height': 535},
    # 'start': datetime.datetime(2018, 10, 12, 19, 0),
    # 'end': datetime.datetime(2018, 10, 13, 2, 0), 'name':
    # 'Savage Road comes to the Dawg House',
    # 'url': 'https://www.eventbrite.com/e/savage-road-comes-to-the-dawg-house-tickets-48141455389?aff=ebapi',
    # 'artist_id': '1MK90Dn9tMbk16g2Vb2NQp',
    # 'artist_name': 'A. Savage'}

    user_id = session['user_info']['user_id']

    user = User.query.filter_by(spotify_user_id=user_id).one()
    

    return render_template("shows.html", data=data, zipcode=zipcode, 
            artists=artists, distance=distance, shows=shows)


@app.route("/account/shows")
def display_user_shows():
    """ shows account page with shows they're going to"""

    user_id = session['user_info']['user_id']

    user = User.query.filter_by(spotify_user_id=user_id).one()

    # look at user.events and verify it doesn't match the one they clicked to say
    # they've already added it.

    if user.events:
        already_going = user.events
    else:
        already_going = "You haven't saved any shows before now!"

    shows = request.args.getlist('shows')

    print("THIS IS YOUR SHOW LIST", shows)

    print("THIS IS YOUR REQUEST DICT", request.args.getlist("_artist_id"))

    if shows:
        for show in shows:
            artists = db.session.query(Artist).filter(Event.eventbrite_event_id==show).all()
            # artists at event that way it will be ALL artists at event id
            if show not in [event.eventbrite_event_id for event in user.events]:
                artist = Artist(spotify_artist_id=request.args.get(show+"_artist_id"),
                                name=request.args.get(show+"_artist_name"),
                                art_url=request.args.get(show+"_artist_art_url"),
                                )
                artists.append(artist)

                new_show = Event(eventbrite_event_id=request.args.get(show+"_eventbrite_event_id"),
                                  event_name=request.args.get(show+"_event_name"),
                                  venue_id=request.args.get(show+"_venue_id"),
                                  eventbrite_url=request.args.get(show+"_eventbrite_url"),
                                  logo_url=request.args.get(show+"_logo_url"),
                                  start=request.args.get(show+"_start"),
                                  end=request.args.get(show+"_end"),
                                  users=[user],
                                  artists=artists,
                                )
                db.session.add(new_show)
        db.session.commit()





    # remember to save attached to user --> create new artist/event if it's not there already
    # check to see if event is already there for that person
    # user.events.append(object for event)
    # use relationships instead of raw sql 

    return render_template("hello_shows.html", shows=shows, already_going=already_going)
    # return redirect to new thing.



if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    db.create_all()
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host='0.0.0.0')