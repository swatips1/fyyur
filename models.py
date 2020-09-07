#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    db.UniqueConstraint('name', 'city', 'state', 'address', name='uq_venue')

    shows = db.relationship(
        'Show',
        backref='venue_shows',
        cascade="all, delete",
    )

    def __repr__(self):
        return f'<I am a Venue. My Id is: {self.id},my name is {self.name}, my state is {self.state}, my city is {self.city}, my genres is : {self.genres}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    shows = db.relationship(
        'Show',
        backref='show'
        # ,lazy=True,
        # collection_class= list
        # ,        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<I am an Artist. My Id is: {self.id},my name is {self.name},  my genres is : {self.genres} and my shows are : {self.shows}>'

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id= db.Column(db.Integer,db.ForeignKey('venue.id', name ='fk_venue'), nullable=False)
    artist_id= db.Column(db.Integer,db.ForeignKey('artist.id', name ='fk_artist'), nullable=False)
    show_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    venue = db.relationship(
        'Venue',
        backref='venue',
        lazy=True,
        collection_class= list
        # ,        cascade='all, delete-orphan'
    )

    artist = db.relationship(
        'Artist',
        backref='artist',
        lazy=True,
        collection_class= list
        # ,        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<I am a Show. My Id is: {self.id},my venue is {self.venue} and my artist is : {self.artist}>'

#Enable this section when trying to start over.
# class Venue(db.Model):
#     __tablename__ = 'Venue'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#
#     # TODO: implement any missing fields, as a database migration using Flask-Migrate
#
# class Artist(db.Model):
#     __tablename__ = 'Artist'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
