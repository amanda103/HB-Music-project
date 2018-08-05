import unittest

from server import app
from model import db, example_data, connect_to_db, User, Event
import process
import datetime


from flask_tests import _mock_get_related_artists 


class ProcessTests(unittest.TestCase):
    """testing functions in process file"""

    def setUp(self):
        """Do this before each test"""
        
        connect_to_db(app)
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test"""

        db.session.close()
        db.drop_all()


    def test_process_eventbrite_json(self):
        """tests process of eventbrite json"""

        artists = ['1VfgWum48nwYJcCfdPwWgs']
        data = [{'body': '{"top_match_events": \
                [{"locale": "en_US", \
                "subcategory_id": "3009", \
                "is_series_parent": false, \
                "currency": "USD", \
                "logo": {"crop_mask": {"top_left": {"x": 0, "y": 0}, "width": 2160, "height": 1080}, "original": {"url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F47274209%2F143529889148%2F1%2Foriginal.jpg?auto=compress&s=6f9f606e9d1046d98c59ff06581af605", "width": 2160, "height": 1080}, "id": "47274209", "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F47274209%2F143529889148%2F1%2Foriginal.jpg?h=200&w=450&auto=compress&rect=0%2C0%2C2160%2C1080&s=122af37133d6acb2ef08d9653408c513", "aspect_ratio": "2", "edge_color": "#eee8d8", "edge_color_set": true}, \
                "id": "47683928915", \
                "privacy_setting": "unlocked", \
                "venue_id": "20931164", \
                "user_id": "143529889148", \
                "source": "queue", \
                "tx_time_limit": 480, \
                "show_seatmap_thumbnail": false, \
                "show_colors_in_seatmap_thumbnail": false, \
                "logo_id": "47274209", \
                "start": {"timezone": "America/New_York", "local": "2018-11-06T20:00:00", "utc": "2018-11-07T01:00:00Z"}, \
                "version": "4.0.0", \
                "listed": true, \
                "hide_end_date": true, \
                "status": "live", \
                "description": {"text": "ON SALE: 7/20 @ 10AM ET8PM - 12AM", "html": "<P>ON SALE: 7/20 @ 10AM ET<\\/P><P><BR><\\/P><P>8PM - 12AM<\\/P>"}, \
                "show_pick_a_seat": false, \
                "is_free": false, \
                "organization_id": "143529889148", \
                "ticket_classes": [], \
                "end": {"timezone": "America/New_York", "local": "2018-11-07T06:00:00", "utc": "2018-11-07T11:00:00Z"}, \
                "organizer_id": "8182660460", \
                "tld": ".com", \
                "name": {"text": "Michael Nau @ Elsewhere (Zone One)", "html": "Michael Nau @ Elsewhere (Zone One)"}, \
                "language": "en-us", \
                "created": "2018-07-02T18:14:06Z", \
                "is_locked": false, \
                "changed": "2018-07-30T18:00:29Z", \
                "url": "https://www.eventbrite.com/e/michael-nau-elsewhere-zone-one-tickets-47683928915?aff=ebapi", \
                "shareable": false, \
                "style_id": "86831794", \
                "online_event": false, \
                "is_series": false, \
                "category_id": "103", \
                "is_reserved_seating": false}], \
                "pagination": {"object_count": 1, "page_number": 1, "page_size": 50, "page_count": 1, "has_more_items": false}, \
                "events": [{"name": {"text": "Michael Nau & The Mighty Thread (Cotton Jones) @ Cafe du Nord", "html": "Michael Nau &amp; The Mighty Thread (Cotton Jones) @ Cafe du Nord"}, "description": {"text": "Michael Nau returns this year with an expanded full-band lineup now known as The Mighty Thread, comprised of musicians from all over America who have been a part of his touring and recording life over the past few years. \\u201cWe\\u2019ve all played together in various arrangements over the past few years\\u201d, says Nau. \\u201cWe made a record with this core group last year and did a west coast trip at the end of \\u201917. It was fun and so we want to try and keep it going wherever we can. As such, we\\u2019re going to do a string of shows coming up wherein any show listed as \\u201c\\u2026& the mighty thread\\u201d will be full band shows comprised of Will Brown on keys, Benny Yurco on guitar, Graeme Gibson on drums, Robinson Morse & Evan ApRoberts on bass and hopefully get to release some music featuring these bandmates in the near future\\u201d.", "html": "<P>Michael Nau returns this year with an expanded full-band lineup now known as The Mighty Thread, comprised of musicians from all over America who have been a part of his touring and recording life over the past few years. \\u201cWe\\u2019ve all played together in various arrangements over the past few years\\u201d, says Nau. \\u201cWe made a record with this core group last year and did a west coast trip at the end of \\u201917. It was fun and so we want to try and keep it going wherever we can. As such, we\\u2019re going to do a string of shows coming up wherein any show listed as \\u201c\\u2026&amp; the mighty thread\\u201d will be full band shows comprised of Will Brown on keys, Benny Yurco on guitar, Graeme Gibson on drums, Robinson Morse &amp; Evan ApRoberts on bass and hopefully get to release some music featuring these bandmates in the near future\\u201d.<\\/P>"}, \
                "id": "46990677381", \
                "url": "https://www.eventbrite.com/e/michael-nau-the-mighty-thread-cotton-jones-cafe-du-nord-tickets-46990677381?aff=ebapi", \
                "start": {"timezone": "America/Los_Angeles", "local": "2018-10-16T19:30:00", "utc": "2018-10-17T02:30:00Z"}, \
                "end": {"timezone": "America/Los_Angeles", "local": "2018-10-17T06:00:00", "utc": "2018-10-17T13:00:00Z"}, \
                "organization_id": "220866562708", \
                "created": "2018-06-12T17:45:15Z", \
                "changed": "2018-07-26T18:36:54Z", \
                "capacity": null, \
                "capacity_is_custom": null, \
                "status": "live", \
                "currency": "USD", \
                "listed": true, \
                "shareable": false, \
                "online_event": false, \
                "tx_time_limit": 480, \
                "hide_start_date": null, \
                "hide_end_date": true, \
                "locale": "en_US", \
                "is_locked": false, \
                "privacy_setting": "unlocked", \
                "is_series": false, \
                "is_series_parent": false, \
                "is_reserved_seating": false, \
                "show_pick_a_seat": false, \
                "show_seatmap_thumbnail": false, \
                "show_colors_in_seatmap_thumbnail": false, \
                "source": "queue", \
                "is_free": false, \
                "version": "4.0.0", \
                "logo_id": "46032439", \
                "organizer_id": "14685663046", \
                "venue_id": "20479627", \
                "category_id": "103", \
                "subcategory_id": "3009", \
                "format_id": null, \
                "resource_uri": "https://www.eventbriteapi.com/v3/events/46990677381/", \
                "logo": {"crop_mask": {"top_left": {"x": 0, "y": 0}, "width": 4032, "height": 2016}, "original": {"url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F46032439%2F220866562708%2F1%2Foriginal.jpg?auto=compress&s=530a873ef4d80f29e7b296c3e4ce400c", "width": 4032, "height": 3024}, \
                "id": "46032439", \
                "url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F46032439%2F220866562708%2F1%2Foriginal.jpg?h=200&w=450&auto=compress&rect=0%2C0%2C4032%2C2016&s=6bc055f0ba7b5bad794746451c8f8907", "aspect_ratio": "2", "edge_color": "#020201", "edge_color_set": true}}], \
                "location": {"latitude": "37.010531", "augmented_location": {"city": "Santa Cruz", "region": "California", "country": "United States"}, "within": "160.934400061", "longitude": "-122.117826", "address": "95060"}}',
                'headers': {'Access-Control-Max-Age': '600', 
                'Vary': 'Accept', 'X-Rate-Limit': 
                'token:ZSI3XV6TQYBNNZSEGAUN 22/2000 reset=3533s, key:LEOOKCDI7S7THPPNKD 22/2000 reset=3533s', 
                'Allow': 'GET, HEAD, OPTIONS', 
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Authorization, Content-Type', 
                'Content-Type': 'application/json'}, 
                'code': 200}]
        
        from process import process_eventbrite_json
        assert process_eventbrite_json(data, artists) == {'46990677381': 
                                                         {'event_id': '46990677381', 
                                                          'venue_id': '20479627', 
                                                          'logo': 
                                                         {'url': 'https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F46032439%2F220866562708%2F1%2Foriginal.jpg?auto=compress&s=530a873ef4d80f29e7b296c3e4ce400c', 'width': 4032, 'height': 3024}, 
                                                         'start': datetime.datetime(2018, 10, 16, 19, 30), 
                                                         'end': datetime.datetime(2018, 10, 17, 6, 0), 
                                                         'name': 'Michael Nau & The Mighty Thread (Cotton Jones) @ Cafe du Nord', 
                                                         'url': 'https://www.eventbrite.com/e/michael-nau-the-mighty-thread-cotton-jones-cafe-du-nord-tickets-46990677381?aff=ebapi'}}

    def test_process_related_artists(self):
        """tests process of related artists"""

        user = "amanda"
        artists = _mock_get_related_artists("param1", "param2")

        from process import process_related_artists
        assert process_related_artists(artists, user) == {'1Kssd2mp7BMKGZUUKncUt6': 
                                                         [{'spotify_artist_id': '5q3Rqu9idb7essQqKJ7SOa', 
                                                         'name': 'B Boys', 
                                                         'art_url': 'https://i.scdn.co/image/8c9796ef14a930377932988282f625f660b300e0', 
                                                         'users': ['amanda']}, 
                                                         {'spotify_artist_id': '2VhVBXSB8n2KxuzKVZNxTY', 
                                                         'name': 'Ought', 
                                                         'art_url': 'https://i.scdn.co/image/d6e148f762bc3bcae113389236b360efba34a2e0', 
                                                         'users': ['amanda']}]}



if __name__ == '__main__':
    unittest.main()