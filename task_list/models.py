from task_list import db, login
from flask_login import UserMixin

class Users(UserMixin, db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	created_on = db.Column(db.DateTime)
	last_online = db.Column(db.DateTime)

	def set_password(self, password):
		self.password = password

	def check_password(self, password):
		return self.password == password

	def get_id(self):
		return self.user_id

	def __repr__(self):
		return f'<User {self.username}>'

@login.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

class Artists(db.Model):
	artist_id = db.Column(db.Integer, primary_key=True)
	artist_spotify_id = db.Column(db.String(100), unique=True)
	artist_name = db.Column(db.String(200))

	def __repr__(self):
		return f'<Artist {self.artist_name}>'

class Labels(db.Model):
	label_id = db.Column(db.Integer, primary_key=True)
	label_name = db.Column(db.String(200))

	def __repr__(self):
		return f'<Label {self.label_name}>'

class Producers(db.Model):
	producer_id = db.Column(db.Integer, primary_key=True)
	producer_name = db.Column(db.String(200))

	def __repr__(self):
		return f'<Producer {self.producer_name}>'

class Albums(db.Model):
	album_id = db.Column(db.Integer, primary_key=True)
	album_spotify_id = db.Column(db.String(100), unique=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'))
	album_name = db.Column(db.String(255))
	album_url = db.Column(db.String(255))
	art_url = db.Column(db.String(255))
	label_id = db.Column(db.Integer, db.ForeignKey('labels.label_id'))
	release_year = db.Column(db.String(25))
	genre = db.Column(db.String(100))

	def __repr__(self):
		return f'<Album {self.album_name}>'

class Tracks(db.Model):
	track_id = db.Column(db.Integer, primary_key=True)
	track_spotify_id = db.Column(db.String(100), unique=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.artist_id'))
	album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'))
	track_number = db.Column(db.Integer)
	track_name = db.Column(db.String(255))
	duration_ms = db.Column(db.Integer)
	producer_id = db.Column(db.Integer, db.ForeignKey('producers.producer_id'))
	track_url = db.Column(db.String(255))
	lyrics_url = db.Column(db.String(255))

	def __repr__(self):
		return f'<Track {self.track_name}>'

class UserAlbumRatings(db.Model):
	__tablename__ = 'user_album_ratings'
	user_album_rating_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'))
	best_track_id = db.Column(db.Integer, db.ForeignKey('tracks.track_id'))
	overall_rating = db.Column(db.Integer)
	production_rating = db.Column(db.Integer)
	unique_rating = db.Column(db.Integer)
	enjoyment_rating = db.Column(db.Integer)
	thoughts = db.Column(db.String())

	def __repr__(self):
		return f'UserAlbumRating {self.album_id} {self.rating}'

class UserTrackRatings(db.Model):
	__tablename__ = 'user_track_ratings'
	user_track_rating_id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	track_id = db.Column(db.Integer, db.ForeignKey('tracks.track_id'))
	rating = db.Column(db.Integer)
	listens = db.Column(db.Integer)
	last_listen = db.Column(db.DateTime)

	def __repr__(self):
		return f'UserTrackRating {self.track_id} {self.rating}'