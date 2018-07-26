import unittest

from server import app
from model import db, example_data, connect_to_db

class AppTests(unittest.TestCase):
    """Tests for my app site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    # def test_no_login

    # def test_login

    # def test_select_artists

    # def test_enter_valid_zipcode

    # def test_enter_invalid_zipcode

    # def test_select_shows


class AppTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """ Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = "amanda123"

        connect_to_db(app)

        db.create_all()
        example_data()

        def _mock_spotify_user_data

        def _mock_spotify_top_artist_data

        def _mock_related_artist_data

        def _mock_eventbrite_shows


        # create the mock functions and where I would apply them

    def tearDown(self):
        """Do at end of every test"""

        db.session.close()
        db.drop_all()

    def test_user(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = '21wmm4r33y7chvtoc67kxxouq'

        result = self.client.get("/account")
        self.assertIn(b"Graham Hill", results.data)
                

    def test_shows(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = '21wmm4r33y7chvtoc67kxxouq'

        result = self.client.get("/account/shows/attending")
        self.assertIn(b"Harvey Mandel", result.data)

    def test_artists(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = '21wmm4r33y7chvtoc67kxxouq'

        result = self.client.get("/account")
        self.assertIn(b"Flo Rida", result.data)

if __name__ == "__main__":
    unittest.main()