#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from sqlalchemy.sql import text
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.dialects import postgresql
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# COMPLETED TODO: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY_DATABASE_URI = 'postgres://nikarichardson:Aveyond000@127.0.0.1:5432/fyyurapp'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI 

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# our association table 


def extract_genres(s): 
    """ extract_genres: Converts an array of characters back to a list of strings with joined characters between the separator , """ 
    # initialize list 
    lst = [] 

    # initialize current string 
    curr = ""

    for x in s: 
        if x == "," and x != "{":
          # if new genre is listed, append former genre
          lst.append(curr)
          # and start a new string for upcoming genre
          curr = ""
        elif x != "{" and x != "}":
          # append the character to the current string
          curr += x  
        elif x == "}":
          # if at end of list, append last genre to list
          lst.append(curr)

    # return list 
    return lst

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)

    ## Required Fields
    name = db.Column(db.String(120),nullable=False,unique=True)
    address = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    seeking_talent = db.Column(db.Boolean,default=True) 

    ## Optional Fields 
    phone = db.Column(db.String(120),nullable=True)
    website = db.Column(db.String(120),nullable=True)
    seeking_description = db.Column(db.String(500),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)

    # Relationship With Shows 
    shows = db.relationship('Show', backref='venue', lazy=True)

    @property
    def past_shows(self):
      now = datetime.now()
      past_shows = [x for x in self.shows if datetime.strptime(
          x.start_time, '%Y-%m-%dT%H:%M') < now]
      return past_shows

    @property
    def upcoming_shows(self):
      now = datetime.now()
      upcoming_shows = [x for x in self.shows if datetime.strptime(
          x.start_time, '%Y-%m-%dT%H:%M') > now]
      return upcoming_shows

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)

    def serialize(self): 
      my_genres = extract_genres(self.genres)
      return { "id":self.id, "name": self.name, "address":self.address, "genres": my_genres, "city": self.city, "state": self.state, "phone": self.phone, "image_link": self.image_link, "website": self.website, "facebook_link": self.facebook_link, "seeking_talent": self.seeking_talent, "seeking_description": self.seeking_description, "past_shows": self.past_shows, "past_shows_count": self.past_shows_count, "upcoming_shows": self.upcoming_shows, "upcoming_shows_count":self.upcoming_shows_count }

  
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)

    ## Required Fields
    name = db.Column(db.String,nullable=False,unique=True)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    seeking_venue = db.Column(db.Boolean, default=True)

    ## Optional Fields  
    website = db.Column(db.String(120),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)
    seeking_description = db.Column(db.String(500),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    
    ## Relationship with Shows 
    shows = db.relationship('Show', backref='artist', lazy=True)

    @property
    def past_shows(self):
      now = datetime.now()
      past_shows = [x for x in self.shows if datetime.strptime(
          x.start_time, '%Y-%m-%dT%H:%M') < now]
      return past_shows

    @property
    def upcoming_shows(self):
      now = datetime.now()
      upcoming_shows = [x for x in self.shows if datetime.strptime(
          x.start_time, '%Y-%m-%dT%H:%M') > now]
      return upcoming_shows

    @property
    def past_shows_count(self):
      return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
      return len(self.upcoming_shows)
    
    def serialize(self): 
      my_genres = extract_genres(self.genres)
      return { "id":self.id, "name": self.name, "genres": my_genres, "city": self.city, "state": self.state, "phone": self.phone, "image_link": self.image_link, "website": self.website, "facebook_link": self.facebook_link, "seeking_venue": self.seeking_venue, "seeking_description": self.seeking_description, "past_shows": self.past_shows, "past_shows_count": self.past_shows_count, "upcoming_shows": self.upcoming_shows, "upcoming_shows_count":self.upcoming_shows_count }

class Show(db.Model):
  __tablename__ = 'Show' 
  id = db.Column(db.Integer, primary_key=True)

  ## Required Fields 
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  venue_name = db.Column(db.String(120),nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.String(120),nullable=False)

  ## Optional Fields
  artist_image_link = db.Column(db.String(500),nullable=True)

  @property
  def artist_name(self):
    return Artist.query.get(self.artist_id).name

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

@app.route('/venues')
def venues():
  # displays all existing venues in database organized by location 
  all_cities = db.session.query(Venue.city).distinct(Venue.city)
  data = [] 

  for x in all_cities:
    query = db.session.query(Venue).filter_by(city = x)
    sample = db.session.query(Venue).filter_by(city = x).first() 
    venues = []
    for y in query:
      venues.append({"id": y.id,"name": y.name,"upcoming_shows_count": y.upcoming_shows_count})
    data.append({"city": x[0], "state": sample.state, "venues": venues})
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # provides case insensitive, partial string search of existing search venues 
  search_term = request.form.get('search_term', '')
  search = '%{0}%'.format(search_term)
  query = Venue.query.filter(Venue.name.ilike(search))
  num_count = query.count() 
  venues = []
  for y in query:
    venues.append({"id": y.id,"name": y.name,"upcoming_shows_count": y.upcoming_shows_count})
  
  response = {
    "count": num_count,
    "data": venues 
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=venue.serialize())

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False 
  # inserts form data as a new Venue record in the db 
  form = VenueForm(request.form)

  ## make sure name doesn't already exist.
  duplicate_entry = db.session.query(Venue.id).filter_by(name=form.name.data).scalar() is not None
  if duplicate_entry == True:
    error = True 
    flash('Venue ' + data.name + ' has already been added to this database. Duplicate entries are not permitted.')
  try:
    name = form.name.data
    address = form.address.data 
    city = form.city.data
    state = form.state.data
    genres = form.genres.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website = form.website.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    venue = Venue(name=name,address=address,city=city,state=state,genres=genres,seeking_talent=seeking_talent,phone=phone,website=website,seeking_description=seeking_description,image_link=image_link,facebook_link=facebook_link)  
    db.session.add(venue)
    db.session.commit()

    if not error:
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    error = True
    # on unsuccessful db insert, flash an error instead
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  finally: 
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # deletes a venue based on artist_id using SQL Alchemy 
  error = False
  venue = Venue.query.get(venue_id) 
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True 
    flash('Venue ' + venue.name + ' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error: 
    flash('Venue ' + venue.name + ' was deleted.')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # returns relevant data from querying the database 
  query = db.session.query(Artist)
  data = [] 

  for artist in query:
    data.append({"id": artist.id,"name": artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # provides search functionality on artists with partial string search and case insensitivity
  search_term = request.form.get('search_term', '')
  search = '%{0}%'.format(search_term)
  query = Artist.query.filter(Artist.name.ilike(search))
  num_count = query.count() 
  artists = []

  for y in query:
    artists.append({"id": y.id,"name": y.name,"upcoming_shows_count": y.upcoming_shows_count})
  
  response = {
    "count": num_count,
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # deletes an artist based on artist_id using SQL Alchemy 
  error = False
  artist = Artist.query.get(artist_id) 
  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    error = True 
    flash('Artist ' + artist.name + ' could not be deleted.')
    db.session.rollback()
  finally:
    db.session.close()
  if not error: 
    flash('Artist ' + artist.name + ' was deleted.')

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist with the given artist_id
  artist = Artist.query.get(artist_id)
  return render_template('pages/show_artist.html', artist=artist.serialize())

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # pre-populates form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # updates existing artist record from artist_id using form data
  error = False 
  # use form data to update existing record 
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try: 
      artist.name = form.name.data
      artist.state = form.state.data
      artist.city = form.city.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.website = form.website.data 
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.commit()
   
      if not error:
        # on successful db insert, flash success
        flash('Artist ' + artist.name + ' was successfully updated!')
  except:
    error = True
    db.session.rollback() 
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + artist.name + ' could not be updated')
  finally: 
    db.session.close() 
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id): # form = AddressForm(request.form, country='US')
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # updates existing venue record from venue_id using form data
  error = False 

  get_genres = Venue.query(Venue.genres).filter(Venue.id==venue_id) 
  form = VenueForm(request.form,genres=["Classical"])
  venue = Venue.query.get(venue_id)
  try: 
      venue.name = form.name.data
      venue.state = form.state.data
      venue.city = form.city.data
      venue.address = form.address.data
      venue.genres = form.genres.data
      venue.phone = form.phone.data     
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website.data
      venue.seeking_talent = form.seeking_talent.value
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
      if not error:
        # on successful db insert, flash success
        flash('Venue ' + venue.name + ' was successfully updated!')

  except:
    error = True
    db.session.rollback() 
    # on unsuccessful db update, flash an error instead.
    flash('An error occurred. Venue ' + venue.name + ' could not be updated')
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
  error = False 
  # insert form data as a new VArtist record in the db. 
  form = ArtistForm(request.form)

  ## ensure name doesn't already exist.
  duplicate_entry = db.session.query(Artist.id).filter_by(name=form.name.data).scalar() is not None
  if duplicate_entry == True:
    error = True 
    flash('Artist ' + data.name + ' has already been added to this database. Duplicate entries are not permitted.')
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = form.genres.data
    website = form.website.data 
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    artist = Artist(name=name,city=city,state=state,genres=genres,seeking_venue=seeking_venue,phone=phone,seeking_description=seeking_description,image_link=image_link,facebook_link=facebook_link)  
    db.session.add(artist)
    db.session.commit()
    if not error:
      # on successful db insert, flash success
      flash('Artist ' + form.name.data + ' was successfully listed!')
  except:
    error = True
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally: 
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  data=[]
  for show in shows:
    data.append({"venue_id": show.venue_id,"venue_name": show.venue_name,"artist_id": show.artist_id,"artist_name" : show.artist_name, "artist_image_link": show.artist_image_link, "start_time": show.start_time})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_show_form():
  # renders form; do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False 
  # insert form data as a new show record in the database 
  form = ShowForm(request.form)

  try: 
    venue_id = form.venue_id.data
    venue_name = form.venue_name.data
    artist_id = form.artist_id.data
    start_time = form.start_time.data
    artist_image_link = form.artist_image_link.data
    flash(start_time) 
    # '2020-01-19T11:38:54'
    show = Show(venue_id=venue_id,venue_name=venue_name,artist_id=artist_id,start_time=start_time,artist_image_link=artist_image_link)
    db.session.add(show)
    db.session.commit()
    if not error:
      # on successful db insert, flash success
      flash('Show was successfully listed!')
  except:
    error = True
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally: 
    return render_template('pages/home.html')

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
