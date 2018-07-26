"""Models and database functions for Amanda's app"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of amanda's app"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spotify_user_id = db.Column(db.String(30), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    pic_url = db.Column(db.String(250), nullable=True)

    events = db.relationship("Event", secondary="users_events")
    artists = db.relationship("Artist", secondary="users_artists")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} display_name={self.display_name}>"



class Artist(db.Model):
    """ Movie information"""

    __tablename__ = "artists"

    artist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spotify_artist_id = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    art_url = db.Column(db.String(150), nullable=False)

    events = db.relationship("Event", secondary="artists_events")
    users = db.relationship("User", secondary="users_artists")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Artist artist_id={self.artist_id} name={self.name}>"


class Event(db.Model):
    """Events"""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    eventbrite_event_id = db.Column(db.BigInteger, unique=True, nullable=False)
    event_name = db.Column(db.String(200), nullable=False)
    venue_id = db.Column(db.BigInteger, nullable=False)
    eventbrite_url = db.Column(db.String(250), nullable=False)
    logo_url = db.Column(db.String(250), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)

    artists = db.relationship("Artist", secondary="artists_events")
    users = db.relationship("User", secondary="users_events")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"""<Event event_id={self.event_id} eventbrite_id={self.eventbrite_event_id}>"""


class UsersEvents(db.Model):
    """User's events"""

    __tablename__ = "users_events"
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        primary_key=True,
                        nullable=False)
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.event_id'), 
                         primary_key=True,
                         nullable=False)


class UsersArtists(db.Model):
    """User's artists"""

    __tablename__ = "users_artists"
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        primary_key=True,
                        nullable=False)
    artist_id = db.Column(db.Integer,
                          db.ForeignKey('artists.artist_id'),
                          primary_key=True,
                          nullable=False)


class ArtistsEvents(db.Model):
    """Artist's events"""

    __tablename__ = "artists_events"
    artist_id = db.Column(db.Integer,
                          db.ForeignKey('artists.artist_id'), 
                          primary_key=True,
                          nullable=False)
    event_id = db.Column(db.Integer,
                         db.ForeignKey('events.event_id'),
                         primary_key=True,
                         nullable=False)


def example_data():
    """Create example data for the test database."""
    User.query.delete()
    Artist.query.delete()
    Event.query.delete()

    user1 = User(spotify_user_id='21wmm4r33y7chvtoc67kxxouq',
                 display_name='Graham Hill', pic_url='https://vetstreet.brightspotcdn.com/dims4/default/5b3ffe7/2147483647/thumbnail/180x180/quality/90/?url=https%3A%2F%2Fvetstreet-brightspot.s3.amazonaws.com%2F8e%2F4e3910c36111e0bfca0050568d6ceb%2Ffile%2Fhub-dogs-puppy.jpg')
    user2 = User(spotify_user_id='21wmm4r33y7chvtoc99kxxouq',
                 display_name='Rusty Nail', pic_url='https://www.cesarsway.com/sites/newcesarsway/files/styles/large_article_preview/public/Common-dog-behaviors-explained.jpg?itok=FSzwbBoi')
    user3 =  User(spotify_user_id='21wmm4r33y7chvtoc88kxxouq',
                 display_name='Fred Goodboy', pic_url='https://hips.hearstapps.com/ghk.h-cdn.co/assets/17/30/2560x1280/landscape-1500925839-golden-retriever-puppy.jpg?resize=768:*')
    db.session.add_all([user1, user2, user3])
    artist1 = Artist(spotify_artist_id='0jnsk9HBra6NMjO2oANoPY', 
                    name="Flo Rida",
                    art_url="https://i.scdn.co/image/2d0b5f483c7ed95b7c3c63147c3d38f9366b2c21")
    artist2 = Artist(spotify_artist_id='6MF9fzBmfXghAz953czmBC', 
                    name="Taio Cruz",
                    art_url="https://i.scdn.co/image/dedc6fcfc7ec914af993c783a60a8f34bdcfaa01")
    artist3 = Artist(spotify_artist_id="085pc2PYOi8bGKj0PNjekA", 
                    name="will.i.am",
                    art_url="https://i.scdn.co/image/d9e6047498dc100048c4597be2aa1d20ebf6df40")
    db.session.add_all([artist1, artist2, artist3])
    event1 = Event(eventbrite_event_id=47282798122,
                    event_name='Harvey Mandel',
                    venue_id=17707560,
                    eventbrite_url='https://www.eventbrite.com/e/harvey-mandel-tickets-47282798122?aff=ebapi',
                    logo_url='https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F46352034%2F57113820621%2F0%2Foriginal.jpg?auto=compress&s=f0cc3a3bff6c9e148776d53faf859aea',
                    start=datetime(2018, 8, 12, 17, 0),
                    end=datetime(2018, 8, 12, 23, 30),
                    )
    event2 = Event(eventbrite_event_id=43327655183,
                    event_name='Blackie Farrell',
                    venue_id=23148822,
                    eventbrite_url='https://www.eventbrite.com/e/blackie-farrell-tickets-43327655183?aff=ebapi',
                    logo_url='https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F41116425%2F19508933240%2F1%2Foriginal.jpg?auto=compress&s=ce6ca8779fb27a161884ee8ee467ef45',
                    start=datetime(2018, 7, 28, 19, 0),
                    end=datetime(2018, 7, 28, 21, 0),
                    )
    event3 = Event(eventbrite_event_id=47828245570,
                    event_name='Marisa Anderson @ Cafe du Nord',
                    venue_id=20479627,
                    eventbrite_url='https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F47149275%2F220866562708%2F1%2Foriginal.jpg?auto=compress&s=d089677775de2ca1c9bdeec5909cd0f0',
                    logo_url='https://www.eventbrite.com/e/marisa-anderson-cafe-du-nord-tickets-47828245570?aff=ebapi',
                    start=datetime(2018, 8, 8, 19, 30),
                    end=datetime(2018, 8, 9, 6, 0),
                    )
    db.session.add_all([event1, event2, event3])

    artist1.events = [event1]
    artist2.events = [event2]
    artist3.events = [event3]

    user1.artists = [artist1, artist2, artist3]
    user2.artists = [artist1, artist2, artist3]
    user3.artists = [artist1, artist2, artist3]

    user1.events = [event1]
    user2.events = [event2]
    user3.events = [event3]

    # db.session.add_all([user1, user2, user3, artist1, artist2, artist3, 
    #                     event1, event2, event3, artist1.events, artist2.events,
    #                     artist3.events, user1.artists, user2.artists,
    #                     user3.artists, user1.events, user2.events, user3.events])
    db.session.commit()




##############################################################################
# Helper functions

def connect_to_db(app, uri='postgresql:///testdb'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print("Connected to DB.")