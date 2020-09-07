#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
#
# import json
import dateutil.parser
import babel
from datetime import datetime
#Import all models
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

# app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Supporting functions.
#----------------------------------------------------------------------------#
#Get count of past or upcoming shows
def count_shows(shows, type):
    show_count=0
    for each_show in shows:
        if type =='upcoming' and datetime.now() > each_show.show_datetime:
            show_count = show_count + 1
        if type =='past' and datetime.now() < each_show.show_datetime:
            show_count = show_count + 1
    return show_count

#Populate the list of past and upcoming shows
def populate_shows(shows, past_shows, upcoming_shows):
    for each_show in shows:
        venue = each_show.venue
        if datetime.now() > each_show.show_datetime:
            # if any(d['venue_id'] == venue.id for d in past_shows):
            #     a=1
            # else:
            past_shows.append({
              "venue_id": venue.id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": str(each_show.show_datetime)
            })
        else:
            # if any(d['venue_id'] == venue.id for d in upcoming_shows):
            #     a=1
            # else:
            upcoming_shows.append({
              "venue_id": venue.id,
              "venue_name": venue.name,
              "venue_image_link": venue.image_link,
              "start_time": str(each_show.show_datetime)
            })

def is_duplicate_venue(name, city, state, address):
    return Venue.query.filter_by(address=address).filter_by(name=name).filter_by(city=city).filter_by(state=state).count()
