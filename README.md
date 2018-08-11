*[ShowSpotter](http://www.showspotter.org)*
=============

Summary
-------
ShowSpotter is a web app geared toward folks looking to expand their music library outside of their headphones! 
This app allows users to see upcoming concerts in their area that are based on their personal musical preference. 
ShowSpotter uses Spotify's OAuth 2.0 authentication system for login and queries the Spotify API for the user's 
top artists to display. Once the preferred artists are selected the app queries the Eventbrite API to find relevant 
upcoming shows within the area. Users are able to save shows they’re interested in attending and see which shows other 
users are attending.

About the Developer
-------
ShowSpotter was created by Amanda Cameron. Learn more about the developer on [LinkedIn](http://www.linkedin.com/in/amandacameron103)

Table of Contents
-------
* [Tech Stack](#tech-stack)
* [Features](#features)
* [Setup/Installation](#install)
* [To-Do](#future)

<a name="tech-stack"></a>Technologies
-------
Tech Stack:
- Python
- Flask
- Python unittest framework
- Jinja2
- PostgreSQL
- SQLAlchemy
- JavaScript
- jQuery
- AJAX
- OAuth2
- HTML
- CSS
- Bootstrap
- Spotify API
- Eventbrite API

<a name="features"></a>Features
-------

Users log into ShowSpotter site with Spotify. By using OAuth to validate their credentials
the postgres database only stores a users public profile information and 
not maintain separate records for user login. After logging in, ShowSpotter queries 
Spotify for the user’s top five artists.
![login](http://g.recordit.co/tQVwi6oS6j.gif)

Users are also able to search for related artists With the help of a jQuery event listener 
and AJAX to retrieve and format the data from Spotify.
![related-artists](http://g.recordit.co/0HC4UrkBOl.gif)

Once the user has selected all the artists they're interested in they enter their zipcode
which is validated via regular expression.
![zipcode](http://g.recordit.co/UMN1meIyqL.gif)

The artist information is sent to Eventbrite and the shows are displayed for the user.
![shows](http://g.recordit.co/OMzsvKF59w.gif)

Once the user has saved a show, the show image will appear on the My Shows page in a chronological
carousel.
![my-shows](http://g.recordit.co/uq1lwIRcdl.gif)

If other users are also attending a show that has been saved, the user will see their friend's
picture displayed below the show carousel. By clicking on a profile picture the user is 
redirected to thtat person's page of saved shows. This is accomplished by a SQLAlchemy
query to the association table set up in the relational database.
![other-users](http://g.recordit.co/KnX74i8638.gif)

When browsing another user's page, the user has the option to save shows to their own profile.
![add-shows](http://g.recordit.co/6e3GzhVBZ7.gif)


<a name="future"></a>For Version 2.0
-------
- Add to Google Calendar feature
- Incorporate SeatGeek API to have additional coverage of artist events