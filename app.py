#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from sqlalchemy import Column, Integer, DateTime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import app, db, Venue, Artist, Shows
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


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

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
 # TODO: replace with real venues data.
 #  num_shows should be aggregated based on number of upcoming shows per venue.
@app.route('/venues')
def venues():
  data = []
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  for city in cities:
    venues_in_city = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(
        Venue.state == city[1])
    data.append({
        "city": city[0],
        "state": city[1],
        "venues": venues_in_city
    })
      
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(search_term))).all()
  response = {
    "count": len(venues),
    "data": venues
    }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  upcoming_shows_count = db.session.query(Shows).join(Artist).filter(Shows.c.venue_id == venue_id).filter(Shows.c.date > datetime.now()).all()
  upcoming_shows = []
  past_shows_count = db.session.query(Shows).join(Artist).filter(Shows.c.venue_id == venue_id).filter(Shows.c.date < datetime.now()).all()
  past_shows = []

  for show in past_shows_count:
    past_shows.append({
        "artist_id": show.artist_id,
        "artist_name":Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": show.date.strftime("%m/%d/%Y, %H:%M:%S")
    })
    for show in upcoming_shows_count:
      upcoming_shows.append({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.get(show.artist_id).name,
          "artist_image_link": Artist.query.get(show.artist_id).image_link,
          "start_time": show.date.strftime("%m/%d/%Y, %H:%M:%S")
      })
  
  data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "past_shows" : past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    form = VenueForm()
    new_venue = Venue(
      name=form.name.data,
      city=form.city.data,
      genres=form.genres.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,     
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data,
      website=form.website.data,
    )
    db.session.add(new_venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    db.session.close()
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.filter_by(id=venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The venue has been removed together with all of its shows.')
    return render_template('pages/home.html')
  except ValueError:
    db.session.rollback()
    flash('It was not possible to delete this Venue')
  finally:
    db.session.close()
  return None


#  Artists
#  ----------------------------------------------------------------
# TODO: replace with real data returned from querying the database
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
    add= {
        'id' : artist.id,
        'name' : artist.name
    }
    data.append(add)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist_search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(
        Artist.name.ilike('%{}%'.format(artist_search_term))).all()
  response = {
    "count": len(artists),
    "data": artists
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist().query.get(artist_id)
  upcoming_shows_count = db.session.query(Shows).join(Venue).filter(Shows.c.artist_id == artist_id).filter(
      Shows.c.date > datetime.now()).all()
  upcoming_shows = []
  past_shows_count = db.session.query(Shows).join(Venue).filter(Shows.c.artist_id == artist_id).filter(
        Shows.c.date < datetime.now()).all()
  past_shows = []

  for show in past_shows_count:
      past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": Venue.query.get(show.venue_id).name,
          "venue_image_link": Venue.query.get(show.venue_id).image_link,
          "start_time": show.date.strftime("%m/%d/%Y, %H:%M:%S")
      })

  for show in upcoming_shows_count:
      upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": Venue.query.get(show.venue_id).name,
          "venue_image_link": Venue.query.get(show.venue_id).image_link,
          "start_time": show.date.strftime("%m/%d/%Y, %H:%M:%S")
      })

  data = {
      'id' : artist.id,
      'name' : artist.name,
      'city' : artist.city,
      'state' : artist.state,
      'phone' : artist.phone,
      'genres' : [artist.genres],
      'image_link' : artist.image_link,
      'facebook_link' : artist.facebook_link,     
      'past_shows' : past_shows,
      'upcoming_shows' : upcoming_shows,
      'past_shows_count' : len(past_shows),
      'upcoming_shows_count' : len(upcoming_shows)
      }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  try :
    artist.name = form.name.data
    artist.genres = ','.join(form.genres.data)
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone=form.phone.data
    artist.facebook_link=form.facebook_link.data
    artist.image_link=form.image_link.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))




@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue().query.get(venue_id)
  try:
    venue = Venue().query.get(venue_id)
    venue.name = form.name.data
    venue.genres = ','.join(form.genres.data)
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone=form.phone.data
    venue.facebook_link=form.facebook_link.data
    venue.image_link=form.image_link.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + 'was successfully updated!')
  except:
    db.session.rollback()
    flash(f'An error occurred.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  try:
    newArtist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            website=form.website.data,
             )
    db.session.add(newArtist)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  for show in db.session.query(Shows).all():
    artist = Artist().query.get(show.artist_id)
    venue = Venue().query.get(show.venue_id)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": (show.date).strftime("%m/%d/%Y, %H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show_form = ShowForm(request.form)
  try:
    new_show = Shows.insert().values(venue_id=show_form.venue_id.data, artist_id=show_form.artist_id.data, date=show_form.start_time.data)
    db.session.execute(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. ')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
