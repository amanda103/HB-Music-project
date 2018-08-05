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

SPOTIFY_APP_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_APP_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
eventbrite_token = os.environ["EVENTBRITE_TOKEN"]
eventbrite_url = "https://www.eventbriteapi.com/v3/"


app = Flask(__name__)
# app.debug = True
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
    """Make sure user is logged in and if not, redirect"""
    endpoints = ['login', 'spotify_authorized', 'show_acct_info']
    if 'user_info' not in session and request.endpoint not in endpoints:
        return redirect(url_for('login'))

@app.route('/')
def index():
    """Homepage redirects to login"""
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Login via spotify credentials"""
    callback = url_for(
        'spotify_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
        )
    return spotify.authorize(callback=callback)


@app.route('/login/authorized')
def spotify_authorized():
    """Spotify authorization"""

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

@spotify.tokengetter
def get_spotify_oauth_token():
    """Get's token every time"""

    return session.get('oauth_token')


@app.route("/logout")
def logout():
    """Logout"""
    #TODO - make a button to let users do this without having to go to the route
    # directly
    del session['oauth_token']
    flash("Logout successful")

    return render_template("homepage.html")

@app.route("/account")
def show_acct_info():
    """First page user sees after login, displays top artists and account info"""

    user = get_user_object()

    if user:
        flash("WELCOME BACK")
    else:
        user = User(spotify_user_id=session['user_info']['user_id'],
                    pic_url=session['user_info']['user_pic_url'],
                    display_name=session['user_info']['user_display_name'])
        db.session.add(user)
        db.session.commit()

    items = gets_user_top_artists(user)
    #TODO
    #only getting the first image - is this important? idk
    #only saving the top artists - not related artiests

    return render_template("hello.html", artists_info=items)



# TODO: store seached artists in session, once they pick a show 
# with that artist then add artist to db


@app.route("/related-artists")
def display_related_artists():
    """Grabs related artists by pinging spotify with artist id selected via img"""

    user = get_user_object()

    artist_id = request.args.get('artist_id')

    related_artists = get_related_artists(artist_id, user)

    from process import process_related_artists

    related_artists_dict = process_related_artists(related_artists, user)

    return render_template("related-artists.html", related_artists_dict=related_artists_dict)   

@app.route("/friends")
def display_concert_goers():
    """Gets other users already going to the same concert"""

    event_id = request.args.get('show_id')

    friends = []
    event_obj = db.session.query(Event).filter(Event.eventbrite_event_id == event_id).first()
    if event_obj:
        people = event_obj.users
        if people:
            for p in people:
                if p.spotify_user_id == session['user_info']['user_id']:
                    continue
                else:
                    friends.append(p)

    return render_template("friends.html", people=friends)


@app.route("/search-events")
def display_top_artist_events():
    """searches for top artists on eventbrite"""

    user = get_user_object()

    zipcode = request.args.get('zipcode')

    distance = "100mi"
   
    artists_by_id = request.args.getlist("search-events-artists")

    artists_by_name = []

    session['user_artists'] = {}
    
    if artists_by_id:
        for artist_id in artists_by_id:
            name = request.args.get(artist_id+"_artist_name")
            artists_by_name.append(name)
            art_url = request.args.get(artist_id+"_artist_art_url")
            session['user_artists'][artist_id] = {"name": name,
                                             "art_url": art_url}
        data = get_eventbrite_json(artists_by_name, distance, zipcode)

    else:
        return redirect("/account")

    from process import process_eventbrite_json
    
    shows = process_eventbrite_json(data, artists_by_id)

    return render_template("shows.html", zipcode=zipcode, 
                            distance=distance, shows=shows, artists_by_name=artists_by_name)


@app.route("/account/shows")
def process_user_shows():
    """processes selected shows and redirects to display shows user is attending"""

    user = get_user_object()

    shows = request.args.getlist('shows')

    if shows:
        for show in shows:
            show_there = db.session.query(Event).filter(Event.eventbrite_event_id==show).first()
            if show_there and show not in [event.eventbrite_event_id for event in user.events]:
                user.events.append(show_there)
            else:
                new_show = Event(eventbrite_event_id=request.args.get(show+"_eventbrite_event_id"),
                                  event_name=request.args.get(show+"_event_name"),
                                  venue_id=request.args.get(show+"_venue_id"),
                                  eventbrite_url=request.args.get(show+"_eventbrite_url"),
                                  logo_url=request.args.get(show+"_logo_url"),
                                  start=request.args.get(show+"_start"),
                                  end=request.args.get(show+"_end"),
                                  users=[user],
                                )
                db.session.add(new_show)
        db.session.commit()

    return redirect("/account/shows/attending")

@app.route("/account/shows/attending")
def display_user_shows():
    """Shows user which events they're going to"""

    user = User.query.filter_by(spotify_user_id=session['user_info']['user_id']).one()

    shows = db.session.query(Event).order_by(Event.start.asc()).all()


    upcoming_shows_chron = []

    for show in shows:
        if show in user.events and show.start > datetime.today():
            upcoming_shows_chron.append(show)

    return render_template("hello_shows.html", shows=upcoming_shows_chron)

##############################################################################
# HELPER FUNCTIONS BELOW!
#TODO: add doctests to helpers

def grab_user_info():
    """Get's user info from spotify and puts in session"""

    me = spotify.get('v1/me').data

    user_id = me['id']

    if me['images']:
        image = me['images'][0]['url']
    else:
        image = 'http://www.whothehelldoeshethinkheis.com/wp-content/uploads/2014/03/Homer-Simpsons-Music-Headphones-Anime.jpg'

    if me['display_name']:
        name = me['display_name']
    else:
        name = me['id']

    session['user_info'] = {'user_id' : me['id'],
                            'user_display_name' : name,
                            'user_followers' : me['followers']['total'],
                            'user_pic_url' : image
                            }
    #FIXME do i need to delete here?
    # del session['user_artists']

    return

def get_user_object():
    """Queries db for user object using user info in session"""

    grab_user_info()

    user = db.session.query(User).filter(User.spotify_user_id == session['user_info']['user_id']).first()
    
    return user

def gets_user_top_artists(user):
    """Pulls user's top artists from spotify returns json"""

    scope = 'user-top-read'

    items = spotify.get('v1/me/top/artists?time_range=short_term&limit=5&offset=1').data['items']
    
    return items


def add_artist_users_artists(user, items):
    for item in items:
        if item['id'] not in [artist.spotify_artist_id for artist in user.artists]:
            artist = Artist(spotify_artist_id=item['id'],
                        name=item['name'],
                        art_url=item['images'][0]['url'],
                        users=[user])
            db.session.add(artist)
        else:
            artist = db.session.query(Artist).filter(Artist.spotify_artist_id == item['id']).one()
            artist.users.append(user)
    db.session.commit()


def get_related_artists(artist_id, user):
    """Gets related artists based on users selection"""


    related_artists_dict = {}
    related_artists = spotify.get('v1/artists/{}/related-artists'.format(artist_id)).data
    related_artists_dict[artist_id] = related_artists


    return related_artists_dict

def get_eventbrite_json(artists, distance, zipcode):
    """Get's data as json from eventbrite"""
    
    requests_list = []
    for artist in artists:
        artist = "+".join(artist.split())
        evt_request = {"method": "GET",
                       "relative_url": "events/search/",
                       "body":"token={}&q={}&location.address={}&location.within={}&categories=103"
                       .format(eventbrite_token, artist, zipcode, distance)
                        }
        requests_list.append(evt_request)


    headers = {'Authorization': 'Bearer ' + eventbrite_token}

    response = requests.post(eventbrite_url+"batch/", 
                            headers=headers,
                            data={"batch": json.dumps(requests_list)})
    data = response.json()

    return data



##############################################################################


if __name__ == '__main__':
    app.debug = True
    connect_to_db(app, 'postgresql:///amandasapp')
    db.create_all()
    app.config['DEBUG'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host='0.0.0.0')