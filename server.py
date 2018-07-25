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

    user = db.session.query(User).filter(User.spotify_user_id == user_id).first()

    if user:
        flash("WELCOME BACK")
    else:
        user = User(spotify_user_id=me['id'], pic_url=me['images'][0]['url'], display_name=me['display_name'])
        db.session.add(user)
        db.session.commit()

    scope = 'user-top-read'

    items = spotify.get('v1/me/top/artists?time_range=short_term&limit=50&offset=1').data['items']

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
        

    #only getting the first image - is this important? idk

    return render_template("hello.html",
                            artists_info=items,
                            )



@spotify.tokengetter
def get_spotify_oauth_token():

    return session.get('oauth_token')


@app.route("/logout")
def logout():
    del session['oauth_token']
    flash("Logout successful")

    return render_template("homepage.html")

# get related artists
# handle (AJAX) requests from client 
# client will send a single artist id
# server will look up related artists via spotify api
# sever will return a chunk of html to the client
@app.route("/related-artists")
def display_related_artists():

    user_id = session['user_info']['user_id']

    user = User.query.filter_by(spotify_user_id=user_id).one()

    artist_id = request.args.get('artist_id')

    # selected_artists = request.args.getlist("artist-ids")
    # no longer want to do this for all of them - do dynamically one at a time once
    # user clicks picture! have to rehash the related_artists_dict below then...

    from process import process_related_artists

    related_artists_dict = {}
    # for artist_id in selected_artists:
    related_artists = spotify.get('v1/artists/{}/related-artists'.format(artist_id)).data
    related_artists_dict[artist_id] = related_artists

    related_artists = process_related_artists(related_artists_dict, user)
    # return render_template("related_artists.html", related_artists=related_artists)
    # how to move this over to the jinja template and into new html???
    # return render_template("related-artists.html", related_artists=related_artists)

    return render_template("related-artists.html", related_artists=related_artists)   

@app.route("/search-events")
def display_top_artist_events():
    """searches for top artists on eventbrite"""

    user_id = session['user_info']['user_id']

    user = User.query.filter_by(spotify_user_id=user_id).one()

    zipcode = request.args.get('zipcode')
    # import zipcodes
    # if zipcodes.is_valid(zipcode):
    #     continue
    # else:
        # what to do if zipcode isn't valid!! don't reload!
    # pull this function out and put it in process file --> but what to do if it's not
    # valid?? Probably prevent default?? Who knows.

    distance = "100mi"
    # hardcoded now but maybe give user option once I have more artists to search
    
    
    artists = request.args.getlist("search-events-artists")
    requests_list = []
    if artists:
        for artist in artists:
            artist = "+".join(artist.split())
            evt_request = {"method": "GET",
                           "relative_url": "events/search/",
                           "body":"token={}&q={}&location.address={}&location.within={}&categories=103".format(eventbrite_token, artist, zipcode, distance)
                            }
            requests_list.append(evt_request)
    else:
        return redirect("/account")


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

    return render_template("shows.html", data=data, zipcode=zipcode, 
            artists=artists, distance=distance, shows=shows, selected_artists=artists)


@app.route("/account/shows")
def process_user_shows():
    """processes selected shows and redirects to viewpage"""

    user_id = session['user_info']['user_id']

    user = User.query.filter_by(spotify_user_id=user_id).one()

    shows = request.args.getlist('shows')

    if shows:
        for show in shows:
            artists = db.session.query(Artist).filter(Event.eventbrite_event_id==show).all()
            # artists at event that way it will be ALL artists at event id
            # add line about artist in db or no to be sure that the artist get's added
            if show not in [event.eventbrite_event_id for event in user.events]:
                # this keeps throwing an error -- why is it still showing me shows that are
                # alreday in db??

                is_artist_there = db.session.query(Artist).filter(Artist.spotify_artist_id == request.args.get(show+"_artist_id")).first()
                if is_artist_there:
                    artists.append(is_artist_there)
                else:
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

    return redirect("/account/shows/attending")

@app.route("/account/shows/attending")
def display_user_shows():
    """Shows user which events they're going to"""

    user = User.query.filter_by(spotify_user_id=session['user_info']['user_id']).one()

    return render_template("hello_shows.html", shows=user.events)




if __name__ == '__main__':
    app.debug = True
    connect_to_db(app)
    db.create_all()
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    app.run(host='0.0.0.0')