#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
# from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import *

#Migration
from flask_migrate import Migrate

#Validation related imports
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect

#Import exceptions
from sqlalchemy import exc

#Import all modesl
from models import *

#Supporting functions
from lib import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# Notes: A lot of googling and research went into making different parts of the project work.
# Yet, no code has been copied from internet. Most of it was to understand how to apply different comcept.
# Main souces were stockoverflow, google, sqlAlchemy documentation, flask documentation and albemic documentation

app = Flask(__name__)

# moment = Moment(app)
csrf = CSRFProtect(app)
app.config.from_object('config')
csrf.init_app(app)
app.jinja_env.filters['datetime'] = format_datetime

# connect to a local postgresql database
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

# *****************************************************************
# Venues
# *****************************************************************

# List all Venues
# -----------------------------------------------------------------
@app.route('/venues')
def venues():
  data0=[]
  venues = Venue.query.order_by('state', 'city').all()
  for each_venue in venues:
      if not any(d['city'] == each_venue.city and d['state'] == each_venue.state for d in data0):
          venue_list =[]
          children = Venue.query.filter_by(state=each_venue.state).filter_by(city=each_venue.city).all()
          for child in children:
              upcoming_shows_count =0
              if any(d['name'] == child.name for d in venue_list):
                  a = 1
              else:
                  upcoming_shows_count = count_shows(child.shows, 'upcoming')
                  venue_list.append({
                  "id": child.id,
                  "name": child.name,
                  "num_upcoming_shows": upcoming_shows_count
                  })
          data0.append({
          "city": each_venue.city,
          "state":each_venue.state,
          "venues": venue_list
          })
  return render_template('pages/venues.html', areas=data0);

# Get a list of all venues with names like search string.
# The match will be case insensitive
# -----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  response = {}
  data =[]
  try:
      venue_name = '%' + request.form.get('search_term', '') + '%'
      venues = Venue.query.filter(Venue.name.ilike(venue_name)).all()
      for each_venue in venues:
          data.append({
              "id" : each_venue.id,
              "name": each_venue.name
          })
      response={
          "count": len(data),
          "data": data
        }
      return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  except Exception as e:
      flash(e)
      flash("No venue matched the search criteria")
      # return render_template('pages/venues.html')
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# Get details of selected venue by id
# -----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows =[]
  upcoming_shows =[]
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  populate_shows(venue.shows, past_shows, upcoming_shows)
  data0 = {
    "id": venue.id,
    "name": venue.name,
    "genres":venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data0)

# Create a new venue
# -----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_submission():
    # Create a new venue. The form data has been validated for data types and existence.
    # Here, we will validate the data for business rules such as duplicates.

    try:
        venueForm = VenueForm(request.form)
        if venueForm.validate_on_submit():
            venue = Venue()
            venue.name = venueForm.name.data
            venue.city = venueForm.city.data
            venue.state = venueForm.state.data
            venue.address = venueForm.address.data
            venue_cnt=is_duplicate_venue(venue.name, venue.city, venue.state, venue.address)
            # venue_cnt =Venue.query.filter_by(address=venue.address).filter_by(name=venue.name).filter_by(city=venue.city).filter_by(state=venue.state).count()
            if (venue_cnt > 0):
                flash("Venu " + venue.name + " at " + venue.address + " already exists in " + venue.city + "," + venue.state + ".Please validate your input.")
                return render_template('forms/new_venue.html', form=venueForm)
            venue.phone = venueForm.phone.data
            venue.genres = venueForm.genres.data
            venue.facebook_link = venueForm.facebook_link.data
            venue.image_link = venueForm.image_link.data
            venue.website = venueForm.website.data
            venue.seeking_talent = venueForm.seeking_talent.data
            venue.seeking_description = venueForm.seeking_description.data if venue.seeking_talent else ""
            try:
                db.session.add(venue)
                db.session.commit()
                flash('Venue ' + venueForm.name.data + ' was successfully listed!')
            except exc.IntegrityError as e:
                flash('Specified Venue already exists. Please correct the information and try again.')
                return render_template('forms/new_venue.html', form=venueForm)
            except exc.DataError as e:
                flash('Please specify ID of the Venue and Artist in the respective fields and try again.')
                return render_template('forms/new_venue.html', form=venueForm)
            except Exception as e:
                flash(e)
                flash('An error occurred. Venue ' + venueForm.name.data + ' could not be created.')
                return render_template('pages/home.html')
        else:
            flash(venueForm.errors)
    except Exception as e:
        flash("error when instantiating form")
        flash(e)
    return render_template('pages/home.html')


# Edit existing venue
# -----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # Edit existing venue. Find data for selected venue id and load it on the form.

  venue = Venue.query.filter_by(id=venue_id).all()[0]
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Persist the changes made to the artist.

  venue = Venue.query.filter_by(id=venue_id).all()[0]
  form = VenueForm(request.form)
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

# Delete existing venue
# -----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # When the user clicks on delete icon on the venue, the
  venue = Venue.query.get(venue_id)
  try:
      venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
      db.session.delete(venue)
      db.session.commit()
      flash("Venue " + str(venue_id) + " was deleted successfully!")
  except Exception as e:
      flash("error when trying to delete venue")
      flash(e)
  return render_template('pages/home.html')



# *****************************************************************
# End Venues
# *****************************************************************

# *****************************************************************
# Artists
# *****************************************************************

# List all Artists
# -----------------------------------------------------------------
@app.route('/artists')
def artists():
  all_artists=[]
  artists = Artist.query.order_by('id').all()

  for each_artist in artists:
      all_artists.append({
      "id": each_artist.id,
      "name": each_artist.name
        })

  return render_template('pages/artists.html', artists=all_artists)

# Get a list of all artists with names like search string.
# The match will be case insensitive
# -----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  response= {}
  data=[]
  try:
      artist_name = '%' + request.form.get('search_term', '') + '%'
      artists = Artist.query.filter(Artist.name.ilike(artist_name)).all()
      for each_artist in artists:
          data.append({
                "id": each_artist.id,
                "name": each_artist.name
            })
      response ={
        "count": len(data),
        "data":data
      }
  except Exception as e:
      flash(e)
      flash("No artist matched the search criteria")
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Get details of selected artist by id
  the_artist = Artist.query.filter_by(id=artist_id).all()[0]
  past_shows =[]
  upcoming_shows =[]

  populate_shows(the_artist.shows, past_shows, upcoming_shows)
  data0={
        "id": the_artist.id,
        "name": the_artist.name,
        "genres": (the_artist.genres if the_artist.genres else ''),
        "city": (the_artist.city if the_artist.city else ''),
        "state": (the_artist.state if the_artist.state else ''),
        "phone": (the_artist.phone if the_artist.phone else ''),
        "website": (the_artist.website if the_artist.website else ''),
        "facebook_link": (the_artist.facebook_link if the_artist.facebook_link else ''),
        "seeking_venue": the_artist.seeking_venue,
        "seeking_description": the_artist.seeking_description,
        "image_link": (the_artist.image_link if the_artist.image_link else ''),
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

  return render_template('pages/show_artist.html', artist=data0)

# Edit existing artist
# -----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # Edit existing artist. Find data for selected artist id and load it on the form.
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Persist the changes made to the artist.
  form = ArtistForm(request.form)
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data

  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))



#  Create Artist
# -----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['GET','POST'])
def create_artist_submission():
    # Create a new artist. The form data has been validated for data types and existence.
  try:
      artistForm=ArtistForm(request.form)
      if artistForm.validate_on_submit():
          artist = Artist()

          artist.name = artistForm.name.data
          artist.city = artistForm.city.data
          artist.state = artistForm.state.data
          artist.phone = artistForm.phone.data
          artist.genres = artistForm.genres.data
          artist.facebook_link = artistForm.facebook_link.data
          artist.image_link = artistForm.image_link.data
          artist.website = artistForm.website.data
          artist.seeking_venue = artistForm.seeking_venue.data
          artist.seeking_description = artistForm.seeking_description.data if artist.seeking_venue else ""
          print('Going to attempt to create the artist')
          try:
              db.session.add(artist)
              db.session.commit()
              flash('Artist ' + artistForm.name.data + ' was successfully listed!')
              return render_template('pages/home.html')
          except exc.IntegrityError as e:
              flash('Specified show already exists. Please correct the information and try again.')
              return render_template('forms/new_artist.html', form=artistForm)
          except exc.DataError as e:
              flash('Please specify ID of the Venue and Artist in the respective fields and try again.')
              return render_template('forms/new_artist.html', form=artistForm)
          except Exception as e:
              flash('An error occurred. Artist ' + artistForm.name.data + ' could not be created.')
              flash(e)
              return render_template('pages/home.html')
      else:
          flash(artistForm.errors)
  except Exception as e:
      flash("error when instantiating form")
      flash(e)
  return render_template('pages/home.html')


# *****************************************************************
# Shows
# *****************************************************************

# List all Shows
# -----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  all_shows=[]
  shows = Show.query.order_by('id').all()
  for show in shows:
      artist = show.artist
      venue = show.venue
      all_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.show_datetime)
      });
  return render_template('pages/shows.html', shows=all_shows)


# Create new show
# -----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['GET', 'POST'])
def create_show_submission():
  # Create a new show. The form data has been validated for data types and existence.
  # Here, we will validate the data for business rules such as invalid ids.

  show = Show()
  form =None
  try:
      showForm = ShowForm(request.form)
      if showForm.validate_on_submit():
          show.artist_id = showForm.artist_id.data
          show.venue_id = showForm.venue_id.data
          artist_cnt = Artist.query.filter_by(id=show.artist_id).count()
          venue_cnt = Venue.query.filter_by(id=show.venue_id).count()
          if (artist_cnt ==0 or venue_cnt ==0):
              if (artist_cnt ==0 and venue_cnt ==0):
                  flash('Please select a valid venu and artist')
              else:
                  if (venue_cnt ==0):
                      flash('Please select a valid venue')
                  else:
                      flash('Please select a valid artist')
              return render_template('forms/new_show.html', form=showForm)
          show.show_datetime = showForm.start_time.data
          try:
              db.session.add(show)
              db.session.commit()
              flash('Show was successfully listed!')
              return render_template('pages/home.html')
          except exc.IntegrityError as e:
              flash('Specified show already exists. Please correct the information and try again.')
              return render_template('forms/new_show.html')
          except exc.DataError as e:
              flash('Please specify ID of the Venue and Artist in the respective fields and try again.')
              return render_template('pages/home.html')
          except Exception as e:
              print('An error occurred. Show could not be created.')
              flash(e)
              return render_template('pages/home.html')
      else:
          flash(showForm.errors)
  except Exception as e:
      flash("error when instantiating form")
      flash(e)
  return render_template('pages/home.html')

# *****************************************************************
# End Shows
# *****************************************************************

# *****************************************************************
# Error handling
# *****************************************************************
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#****************************************************************************#
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
#****************************************************************************#
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('/errors/CSRFError.html', reason=e.description), 400

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
