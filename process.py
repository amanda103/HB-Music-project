
import json
import pprint
from datetime import datetime
from random import sample, shuffle

def process_eventbrite_json(data, artists):
    """Digests eventbrite json and puts in dict for displaying"""
    
    shows = {}

    shuffle(data)

    for item in data:
        if item['code'] == 200:
            body = json.loads(item['body'])
            events = body['events']
            events = sample((body['events']), len(events)//2)
            for event in events:
                if len(event) > 0:
                    if event.get('logo') is None:
                        logo = "http://cdn6.gurl.com/wp-content/uploads/2012/02/music12.jpg"
                    else:
                        logo = event['logo']['original']
                        start = event['start']['local']
                        start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
                        end = event['end']['local']
                        end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
                        shows[event['id']] = {'event_id' : event['id'],
                                                'venue_id' : event['venue_id'],
                                                'logo' : logo,
                                                'start' : start,
                                                'end' : end,
                                                'name' : event['name']['text'],
                                                'url' : event['url'],
                                                }

    return shows


def process_related_artists(related_artists, user):
    """processes related artists from spotify for helpful info, returns six artists"""

    displayed_artists = {}
    for artist_id, artists in related_artists.items():
        displayed_artists[artist_id] = []

        for value in artists.values():
            if len(value) > 6:
                shuffle(value)
                value = sample(value, 6)
            for v in value:
                if v['images']:
                    image = v['images'][0]['url']
                else:
                    image = "https://ichef.bbci.co.uk/childrens-responsive-ichef-live/r/880/1x/cbbc/guitar.jpg"
                displayed_artists.get(artist_id).append({"spotify_artist_id": v['id'],
                                                         "name": v['name'],
                                                         "art_url": image,
                                                         "users": [user]})
    return displayed_artists

                
        









