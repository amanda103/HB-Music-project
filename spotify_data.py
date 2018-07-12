import sys
import os
import spotipy
import pprint
import json
import spotipy.util as util
from json.decoder import JSONDecodeError
import requests
from spotipy.oauth2 import SpotifyClientCredentials


def finds_user_top_tracks(username):

    scope = 'user-top-read'

    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        ranges = ['short_term', 'medium_term', 'long_term']
        artists = []
        for range in ranges:
            print ("range:", range)
            results = sp.current_user_top_tracks(time_range=range, limit=50)
            for i, item in enumerate(results['items']):
                print (i, item['name'], '//', item['artists'][0]['name'])
                artist_name = item['artists'][0]['name']
                if artist_name not in artists:
                    artists.append(artist_name)
            print()

    return artists

# client_id = os.environ["SPOTIPY_CLIENT_ID"]
# client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
# redirect_uri = os.environ["SPOTIPY_REDIRECT_URI"]

# Get username from terminal
# username = sys.argv[1]

# user id: 21wmm4r33y7chvtoc67kxxouq?si=D7rfBTN8StGeGa9Nn2xP7A
# user id: 21wmm4r33y7chvtoc67kxxouq?si=FMDl01UrQA6MlmtTuvWatQ


# spotifyObj = spotipy.Spotify(auth=token)

# user = spotifyObj.current_user()

# user_name = user['display_name']

# top_tracks = user.current_user_top_artists(time_range=medium_term, limit=50,)

# print(f"user: {user}, user_name: {user_name}, top_tracks: {top_tracks}")