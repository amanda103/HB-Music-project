import unittest

from server import app
from model import db, example_data, connect_to_db, User, Event
import server
import process
import datetime


def _mock_get_user_object():
    user1 = db.session.query(User).filter(User.spotify_user_id == '21wmm4r33y7chvtoc67kxxouq').first()
    return user1

def _mock_gets_user_top_artists(user):
    items = [{'genres': ['preverb'],
              'href':'https://api.spotify.com/v1/artists/0W79ONUwHoehEib1nRXlmi',
              'followers': {'total': 3985, 'href': None},
              'name': 'Angelo De Augustine',
              'external_urls': {'spotify': 'https://open.spotify.com/artist/0W79ONUwHoehEib1nRXlmi'},
              'images': [{'url': 'https://i.scdn.co/image/6e1de75ceeec0017e7b4e8a0b6b9cc5ec187f3cf', 'width': 640, 'height': 640}, {'url': 'https://i.scdn.co/image/f3bd32a468fd5e59af84dd022b7d46c42e88a6e0', 'width': 320, 'height': 320}, {'url': 'https://i.scdn.co/image/405f3aa5510d15a2df4ccb5cc2f4551aa8d72265', 'width': 160, 'height': 160}],
              'popularity': 36,
              'type': 'artist',
              'id': '0W79ONUwHoehEib1nRXlmi',
              'uri':'spotify:artist:0W79ONUwHoehEib1nRXlmi', 
              }]
    return items

def _mock_get_eventbrite_json(param1, param2, param3):
    data = [{"changed": "2018-07-24T21:15:32Z", "locale": "en_US", "subcategory_id": "3009", "is_series_parent": False, "currency": "USD", "id": "44920612762", "logo": {"crop_mask": {"top_left": {"x": 0, "y": 476}, "width": 1364, "height": 682}, "original": {"url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F43221898%2F225372329830%2F1%2Foriginal.jpg?auto=compress&s=bf8d44adac53b9398c6971cde5135e78", "width": 1365, "height": 2048}, "id": "43221898", "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F43221898%2F225372329830%2F1%2Foriginal.jpg?h=200&w=450&auto=compress&rect=0%2C476%2C1364%2C682&s=8f9d839cb3e84c89640fc9c7b7ffdae7", "aspect_ratio": "2", "edge_color": "#8c8c8c", "edge_color_set": True}, "vanity_url": "https://noah-gundersen-space.eventbrite.com", "privacy_setting": "unlocked", "venue_id": "21015749", "user_id": "225372329830", "source": "create_2.0", "tx_time_limit": 480, "show_seatmap_thumbnail": False, "show_colors_in_seatmap_thumbnail": False, "logo_id": "43221898", "start": {"timezone": "America/Chicago", "local": "2018-10-01T19:30:00", "utc": "2018-10-02T00:30:00Z"}, "name": {"text": "Noah Gunderson"}, "version": "3.0.0", "listed": True, "hide_end_date": True, "status": "live", "language": "en-us", "created": "2018-04-06T16:24:10Z", "is_locked": False, "hide_start_date": False, "url": "https://www.eventbrite.com/e/noah-gundersen-acoustic-w-harrison-whitford-tickets-44920612762?aff=ebapi", "shareable": True, "style_id": "84729385", "online_event": False, "is_series": False, "category_id": "103", "is_reserved_seating": True}]
    return data

def _mock_process_eventbrite_json(param1, param2):
    info = {'46990677381': {'event_id': '46990677381', 'venue_id': '20479627', 'logo': {'url': 'https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F46032439%2F220866562708%2F1%2Foriginal.jpg?auto=compress&s=530a873ef4d80f29e7b296c3e4ce400c', 'width': 4032, 'height': 3024}, 'start': datetime.datetime(2018, 10, 16, 19, 30), 'end': datetime.datetime(2018, 10, 17, 6, 0), 'name': 'Michael Nau & The Mighty Thread (Cotton Jones) @ Cafe du Nord', 'url': 'https://www.eventbrite.com/e/michael-nau-the-mighty-thread-cotton-jones-cafe-du-nord-tickets-46990677381?aff=ebapi', 'artist_id': '1VfgWum48nwYJcCfdPwWgs'}}
    return info

def _mock_get_related_artists(param1, param2):
    
    related_artists_dict = {'1Kssd2mp7BMKGZUUKncUt6': {'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/5q3Rqu9idb7essQqKJ7SOa'}, 'followers': {'href': None, 'total': 3527}, 'genres': ['garage psych', 'indie punk', 'preverb'], 'href': 'https://api.spotify.com/v1/artists/5q3Rqu9idb7essQqKJ7SOa', 'id': '5q3Rqu9idb7essQqKJ7SOa', 'images': [{'height': 1000, 'url': 'https://i.scdn.co/image/8c9796ef14a930377932988282f625f660b300e0', 'width': 1000}, {'height': 640, 'url': 'https://i.scdn.co/image/93811fd0a8c10f271d51c021ca56a02a72f6d86d', 'width': 640}, {'height': 200, 'url': 'https://i.scdn.co/image/3d12c18614f9e0a5b4dccd8f027cd37f2c4b0cc9', 'width': 200}, {'height': 64, 'url': 'https://i.scdn.co/image/d387a9ff8e15191b01a30e11f02b73eacb168dc9', 'width': 64}], 'name': 'B Boys', 'popularity': 25, 'type': 'artist', 'uri': 'spotify:artist:5q3Rqu9idb7essQqKJ7SOa'}, {'external_urls': {'spotify': 'https://open.spotify.com/artist/2VhVBXSB8n2KxuzKVZNxTY'}, 'followers': {'href': None, 'total': 25671}, 'genres': ['alternative rock', 'art pop', 'chamber psych', 'dream pop', 'experimental rock', 'freak folk', 'garage psych', 'indie pop', 'indie punk', 'indie rock', 'lo-fi', 'modern rock', 'neo-psychedelic', 'noise pop', 'noise rock', 'nu gaze', 'preverb', 'slow core'], 'href': 'https://api.spotify.com/v1/artists/2VhVBXSB8n2KxuzKVZNxTY', 'id': '2VhVBXSB8n2KxuzKVZNxTY', 'images': [{'height': 640, 'url': 'https://i.scdn.co/image/d6e148f762bc3bcae113389236b360efba34a2e0', 'width': 640}, {'height': 320, 'url': 'https://i.scdn.co/image/29a0b74d92efaa026a71bb4e0a18aae6e43ef3a7', 'width': 320}, {'height': 160, 'url': 'https://i.scdn.co/image/3985e3396db853073de755a9954436434d05064f', 'width': 160}], 'name': 'Ought', 'popularity': 40, 'type': 'artist', 'uri': 'spotify:artist:2VhVBXSB8n2KxuzKVZNxTY'}]}}
    
    return related_artists_dict

def _mock_process_related_artists(param1, param2):

    related_artists ={'0W79ONUwHoehEib1nRXlmi': [{'spotify_artist_id': '7h5ZCPVyKFtXc8NxOVmgMD', 'name': 'Anna St. Louis', 'art_url': 'https://i.scdn.co/image/82d6734b5e7c2313d6777dd351587aa5038a0e28'}]}
    return related_artists


class FlaskTest(unittest.TestCase):
    """Testing my app with connections to db"""

    def setUp(self):
        """Do this before each test"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = "amanda123"
        self.client = app.test_client()
        with self.client as c:
                with c.session_transaction() as sess:
                    sess['user_info'] = {'user_id' : '21wmm4r33y7chvtoc67kxxouq',
                                    'user_display_name' : 'Graham Hill',
                                    'user_followers' : 456,
                                    'user_pic_url' : 'https://vetstreet.brightspotcdn.com/dims4/default/5b3ffe7/2147483647/thumbnail/180x180/quality/90/?url=https%3A%2F%2Fvetstreet-brightspot.s3.amazonaws.com%2F8e%2F4e3910c36111e0bfca0050568d6ceb%2Ffile%2Fhub-dogs-puppy.jpg',
                                    }
                    sess['oauth_token'] = ('BQABuffheFJsh1VgfzmvTpQY3IlDSEFeVuJiKe6oj80B8ktAwgjWHGcALCE_pVVMD-jWsOtDmk3gfMcY3qOJs-d9LarjtUcwtJ_FGyjAKhFLMnBTa5t_LpMCwwJaQ_YWfqEaQagxv5TQr1_fMzsNfs8t8mH0V5cQbMojmbqREw', '')
                    sess['user_artists'] = {'0OdUWJ0sBjDrqHygGUXeCF': {'name': 'Band of Horses',
                                                                        'art_url': 'https://i.scdn.co/image/0f9a5013134de288af7d49a962417f4200539b47'}}
        connect_to_db(app)
        db.create_all()
        example_data()
        server.get_user_object = _mock_get_user_object
        server.gets_user_top_artists = _mock_gets_user_top_artists
        server.get_eventbrite_json = _mock_get_eventbrite_json
        process.process_eventbrite_json = _mock_process_eventbrite_json
        server.get_related_artists = _mock_get_related_artists
        process.process_related_artists = _mock_process_related_artists

    def tearDown(self):
        """Do at end of every test"""

        db.session.close()
        db.drop_all()

    def test_homepage(self):
        """tests redirect on homepage"""
        result = self.client.get("/")
        self.assertIn(b'target URL: <a href="/login">', result.data)

    def test_logout(self):
        """tests whether users can logout"""
        result = self.client.get('/logout')
        self.assertIn(b'Logout successful', result.data)

    def test_login(self):
        """tests login page"""
        result = self.client.get("/login")
        self.assertIn(b'target URL: <a href="https://accounts.spotify.com/authorize?response_type=code&amp;client_id=', result.data)

    def tests_user(self):
        """tests if user info is displayed"""
        result = self.client.get("/account")
        self.assertIn(b'Graham Hill', result.data)

    def test_top_artists(self):
        """ tests display of users top artists"""
        result = self.client.get("/account")
        self.assertIn(b'Angelo De Augustine', result.data )


    def test_displayed_shows_artists(self):
        """tests if selected show is being displayed"""
        result = self.client.get("/search-events?search-events-artists=0W79ONUwHoehEib1nRXlmi&zipcode=95060")
        self.assertIn(b'Michael Nau', result.data)

    def test_displayed_shows_no_artists(self):
        """tests if selected show is being displayed with no artists"""
        result = self.client.get("/search-events?zipcode=95060")
        self.assertNotIn(b'Michael Nau', result.data)
        self.assertIn(b'target URL: <a href="/account">', result.data)

    def test_if_show_selected(self):
        """tests if selected show gets added to shows attending page"""
        user = _mock_get_user_object()
        new_show = Event(eventbrite_event_id=47828245571,
                                  event_name="Amandas show",
                                  venue_id=2348594,
                                  eventbrite_url='https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F47149275%2F220866562708%2F1%2Foriginal.jpg?auto=compress&s=d089677775de2ca1c9bdeec5909cd0f0',
                                  logo_url='https://www.eventbrite.com/e/marisa-anderson-cafe-du-nord-tickets-47828245570?aff=ebapi',
                                  start=datetime.datetime(2018, 8, 8, 19, 30),
                                  end=datetime.datetime(2018, 8, 9, 6, 0),
                                  users=[user]
                                )
        db.session.add(new_show)
        db.session.commit()
        result = self.client.get("/account/shows?47001683300_eventbrite_event_id=47001683300&47001683300_event_name=XXYYXX+%26+SWEATER+BEATS+at+MEZZANINE&47001683300_venue_id=11367224&47001683300_eventbrite_url=https%3A%2F%2Fwww.eventbrite.com%2Fe%2Fxxyyxx-sweater-beats-at-mezzanine-tickets-47001683300%3Faff%3Debapi&47001683300_logo_url=https%3A%2F%2Fimg.evbuc.com%2Fhttps%253A%252F%252Fcdn.evbuc.com%252Fimages%252F46169221%252F149753314296%252F1%252Foriginal.jpg%3Fauto%3Dcompress%26s%3Db5e7531496f76a8630e405a889f2f0a9&47001683300_start=2018-08-03+21%3A00%3A00&47001683300_end=2018-08-04+02%3A00%3A00&47001683300_artist_id=1anyVhU62p31KFi8MEzkbf", follow_redirects=True)
        self.assertIn(b"Amandas show", result.data)

    def test_are_db_shows_displayed(self):
        """tests if shows in db are displayed"""
        result = self.client.get("/account/shows", follow_redirects=True)
        self.assertIn(b'Harvey Mandel', result.data)

    def test_related_artists(self):
        """tests if related artists show up"""
        result = self.client.get("/related-artists")
        self.assertIn(b'Anna St. Louis', result.data)
    
    #TODO:
    # def test_if_no_shows_in_radius(self):




if __name__ == '__main__':
    unittest.main()




