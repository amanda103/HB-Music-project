
import json
import pprint
from datetime import datetime

#TODO: test these! Grab a sample string of json and write unit tests!

# artists= {'A. Savage': {'art_url': 'https://i.scdn.co/image/d9a3b9b797175361e0b018de8b86697074607ad6', 'id': '1MK90Dn9tMbk16g2Vb2NQp', 'related_artist_info': []}, 'Angelo De Augustine': {'art_url': 'https://i.scdn.co/image/6e1de75ceeec0017e7b4e8a0b6b9cc5ec187f3cf', 'id': '0W79ONUwHoehEib1nRXlmi', 'related_artist_info': []}, 'Anna St. Louis': {'art_url': 'https://i.scdn.co/image/82d6734b5e7c2313d6777dd351587aa5038a0e28', 'id': '7h5ZCPVyKFtXc8NxOVmgMD', 'related_artist_info': []}, 'Brigid Mae Power': {'art_url': 'https://i.scdn.co/image/b222dae9d74b890c119aaf3a338072f79e65c79e', 'id': '4uBunSqfCPl9OrLhRifPwK', 'related_artist_info': []}, 'Gun Outfit': {'art_url': 'https://i.scdn.co/image/3054e93eabb195ccae3b4044abb49783156a5fe8', 'id': '4cpsZRPYENvU3QH7kGz4tu', 'related_artist_info': []}, 'Lomelda': {'art_url': 'https://i.scdn.co/image/5149c795f0b7dfa42d13e99695fb00c1c70aae43', 'id': '6zcDLZ62JsbVM1nLrQMzi4', 'related_artist_info': []}, 'Mandolin Orange': {'art_url': 'https://i.scdn.co/image/763a2a83cfe506921e2263415f4f200d1014b904', 'id': '675tsBPpaZtqyiBwEf3ZEP', 'related_artist_info': []}, 'Molly Tuttle': {'art_url': 'https://i.scdn.co/image/24466d8e8c5549e2dc047af471abde02a2fbddaf', 'id': '4LX0KCPnH7gvxEbVXqXmAE', 'related_artist_info': []}, 'Rhiannon Giddens': {'art_url': 'https://i.scdn.co/image/56d6c5fe49a4a8561ae93738675780c930ac9d50', 'id': '1EI0NtLHoh9KBziYCeN1vM', 'related_artist_info': []}, 'Shannon Lay': {'art_url': 'https://i.scdn.co/image/589decd88a711f4a1507f3a1106d9a3dbcbf4736', 'id': '1Kssd2mp7BMKGZUUKncUt6', 'related_artist_info': []}, 'The Stray Birds': {'art_url': 'https://i.scdn.co/image/d49f6bcf785963841f4c6b7a3ce48a69d29a2c2c', 'id': '6cPMzk1hDgzdIe8vkAhcNM', 'related_artist_info': []}}

# data = json.load(open('xxx.json'))
# data = open('xxx.json', 'r').read()
# data = json.loads(data)
def process_eventbrite_json(data, artists):
    """Grabs eventbrite data and returns useful info"""
    

    shows = {}

    for count, item in enumerate(data, 0):
        if item['code'] == 200:
            body = json.loads(item['body'])
            events = body['events']
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
                        shows[event['id']] = ({'event_id' : event['id'],
                                                'venue_id' : event['venue_id'],
                                                'logo' : logo,
                                                'start' : start,
                                                'end' : end,
                                                'name' : event['name']['text'],
                                                'url' : event['url'],
                                                'artist_id' : artists[count],
                                                })
        else:
            continue

    return shows


def process_related_artists(related_artists, user):
    """takes in selected artists, sends to spotify and processes related artists for helpful info"""

    # FIXME
    # truncate dict if it's longer than a certain number
    # so that related artists doesn't display 20 dif artists

    displayed_artists = {}
    for artist_id, artists in related_artists.items():
        displayed_artists[artist_id] = []
        # TODO:
        # while len(displayed_artists[artist_id]) <= 4:
        # still figuring out how to limit the number of related artists I get back
        # that way I don't end up with 20 to display! But maybe that's not a bad thing?
        for value in artists.values():
            for v in value:
                displayed_artists.get(artist_id).append({"spotify_artist_id": v['id'],
                                                         "name": v['name'],
                                                         "art_url": v['images'][0]['url'],
                                                         "users": [user]})
    return displayed_artists

                
        









