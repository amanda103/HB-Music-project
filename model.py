"""Models and database functions for Amanda's app"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of amanda's app"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spotify_user_id = db.Column(db.String(30), unique=True, nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    followers = db.Column(db.Integer, nullable=False)

    event = db.relationship("UsersEvents")
    artist = db.relationship("UsersArtists")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} display_name={self.display_name}>"



class Artist(db.Model):
    """ Movie information"""

    __tablename__ = "artists"

    artist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spotify_artist_id = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(90), nullable=False)
    art_url = db.Column(db.String(150), nullable=False)

    artist = db.relationship("ArtistsEvents")
    user = db.relationship("UsersArtists")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Artist artist_id={self.artist_id} name={self.name}>"


class Event(db.Model):
    """Events"""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    eventbrite_event_id = db.Column(db.BigInteger, unique=True, nullable=False)
    venue_id = db.Column(db.BigInteger, nullable=False)
    eventbrite_url = db.Column(db.String(200), nullable=False)
    logo = db.Column(db.String(200), nullable=True)
    start = db.Column(db.DateTime, nulable=False)
    end = db.Column(db.DateTime, nullable=False)

    artist = db.relationship("ArtistsEvents")
    user = db.relationship("UsersEvents")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Event event_id={self.event_id} eventbrite_id={self.eventbrite_id}>"""


class UsersEvents(db.Model):
    """User's events"""

    __tablename__ = "users_events"
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), primary_key=True, nullable=False)


class UsersArtists(db.Model):
    """User's artists"""

    __tablename__ = "users_artists"
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'), primary_key=True, nullable=False)


class ArtistsEvents(db.Model):
    """Artist's events"""

    __tablename__ = "artists_events"
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'), primary_key=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), primary_key=True, nullable=False)




##############################################################################
# Helper functions

# def connect_to_db(app):
#     """Connect the database to our Flask app."""

#     # Configure to use our PstgreSQL database
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.app = app
#     db.init_app(app)


# if __name__ == "__main__":
#     # As a convenience, if we run this module interactively, it will leave
#     # you in a state of being able to work with the database directly.

#     from server import app
#     connect_to_db(app)
#     print("Connected to DB.")