Fyyur
-----

### Introduction
<img src="https://66.media.tumblr.com/2eb86400f7faba5c7b3991425bbd4cad/9098144b8c09ea53-3b/s1280x1920/7dcac2fda9fcb9e8a0e6087160e588accde2c8bf.png" align="right">

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.



### Completed Work 

* normalized models developed in `app.py`
* form submissions implemented for new Venues, Artists, and Shows
* connects to a local PostgreSQL database  
* button to delete a Venue is available on the Venue page, connects to the /venues/<venue_id> endpoint. 
* artist and venue models are in third normal form with attributes functionally dependent on only the primary key
* controllers for venues, artists, and shows connect to a real database, modeled on the mock data. 
* search endpoints provides app search functionality; search uses partial string matching and is case-insensitive
* artist, show, and venue detail pages are setup
* invalid form submissions are not permitted; required fields are enforced
* referential integrity between models is preserved  

### Tech Stack


* **SQLAlchemy ORM** to be our ORM library of choice
* **PostgreSQL** as our database of choice
* **Python3** and **Flask** as our server language and server framework
* **Flask-Migrate** for creating and running schema migrations
* **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for website's frontend

### Development Setup

First, [install Flask](http://flask.pocoo.org/docs/1.0/installation/#install-flask). 

  ```
  $ cd ~
  $ sudo pip3 install Flask
  ```

To start and run the local development server,

1. Initialize and activate a virtualenv:
  ```
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ virtualenv --no-site-packages env
  $ source env/bin/activate
  ```

2. Install the dependencies:
  ```
  $ pip install -r requirements.txt
  ```

3. Run the development server:
  ```
  $ export FLASK_APP=myapp
  $ export FLASK_ENV=development # enables debug mode
  $ python3 app.py
  ```

4. Navigate to Home page [http://localhost:5000](http://localhost:5000)
