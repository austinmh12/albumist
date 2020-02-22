from flask import Blueprint, flash, redirect, render_template, request, url_for, request, make_response
from task_list.forms import LoginForm, SearchForm, RateAlbumForm
from flask_login import current_user, login_user, logout_user, login_required
from task_list.models import Users, UserAlbumRatings, Albums
import requests
from functools import wraps
from werkzeug.urls import url_parse
from task_list.utilities import *

SPOTIFY_CLIENT_ID = '87a6082e432d47edb46dae2e29d3b6b5'
SPOTIFY_CLIENT_SECRET = 'd8582a4200734009ba26d4134e766520'
RECAPTCHA_PRIVATE_KEY = '6LdZO9kUAAAAAEcdmSBOCeVT8sMvT-HD85CV67Ca'

bp = Blueprint('task_list', __name__)

@bp.route('/')
@login_required
def redir_to_index():
	return index()

@bp.route('/index')
@login_required
def index():
	return render_template('base.html', user=None)

@bp.route('/login', methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('task_list.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash(f'Username Entered: {form.username.data} Actual: {user}')
			flash(f'Password Entered: {form.password.data} Actual: {user.check_password(form.password.data) if user else None}')
			flash('Invalid username or password')
			return redirect(url_for('task_list.login'))
		login_user(user, remember=form.remember_me.data)
		return redirect(url_for('task_list.index'))
	return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('.index'))

@bp.route('/albums/<username>')
@login_required
def albums(username):
	user = Users.query.filter_by(username=username).first_or_404()
	albums_ratings = UserAlbumRatings.query.filter(UserAlbumRatings.user_id == user.user_id)
	print(albums_ratings)
	albums = [(Albums.query.filter(Albums.album_id == albums_rating.album_id).first(), albums_rating) for albums_rating in albums_ratings]
	return render_template('albums.html', user=user, albums=albums)

@bp.route('/spotifyAuth')
def spotify():
	return redirect(spotify_authorization())

@bp.route('/authorized')
def _get_spotify_token():
	code = request.args.get('code')
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('spotifyAuthCode', code)
	spotify_auth_code = request.cookies.get('spotifyAuthCode')
	if spotify_auth_code:
		token = get_spotify_token(spotify_auth_code)
		if token.get('error', None):
			if token.get('error_description') == 'Authorization code expired':
				token = refresh_spotify_token(request.cookies.get('spotifyRefreshToken'))
		resp.set_cookie('spotifyToken', token.get('access_token'))
		if token.get('refresh_token', None):
			resp.set_cookie('spotifyRefreshToken', token.get('refresh_token'))
	return resp

@bp.route('/search', methods=['GET','POST'])
def search():
	form = SearchForm()
	flash(form.validate_on_submit())
	if form.validate_on_submit():
		query = f'album:{form.album_name.data}'
		if form.artist_name.data:
			query += f' artist:{form.artist_name.data}'
		flash(query)
		return redirect(url_for('.show_search', query=query, type=form.type.data if form.type.data else 'album'))
	return render_template('search.html', form=form)

@bp.route('/search_results?query=<query>&type=<type>')
def show_search(query, type='album'):
	token = request.cookies.get('spotifyToken')
	if not token:
		flash('No token. Link your Spotify Account.')
	results = search_spotify(query, type, token)
	if results.get('albums'):
		items = results.get('albums').get('items')
		rets = [(i.get('id'), i.get('artists')[0].get('id'), i.get('images')[0].get('url')) for i in items]
		return render_template('search_results.html', results=rets)
	else:
		flash('No results')
		return redirect(url_for('.search'))

@bp.route('/album/<album_id>')
def album_info(album_id):
	album_details = get_album_info(album_id, request.cookies.get('spotifyToken'))
	artist = ','.join([artist.get('name') for artist in album_details.get('artists')])
	copyrights = album_details.get('copyrights')[0].get('text')
	link = album_details.get('external_urls').get('spotify')
	art = album_details.get('images')[0].get('url')
	name = album_details.get('name')
	label = album_details.get('label')
	release = album_details.get('release_date')
	tracks = [(track.get('track_number'), track.get('name'), track.get('external_urls').get('spotify')) for track in album_details.get('tracks').get('items')]
	rets = (art, link, name, artist, release, label, tracks, copyrights)
	return render_template('album_info.html', details=rets, album_id=album_id)

@bp.route('/album/<album_id>/rate', methods=['GET','POST'])
def rate_album(album_id):
	album_details = get_album_info(album_id, request.cookies.get('spotifyToken'))
	artist = ','.join([artist.get('name') for artist in album_details.get('artists')])
	link = album_details.get('external_urls').get('spotify')
	art = album_details.get('images')[0].get('url')
	name = album_details.get('name')
	tracks = [(track.get('id'), track.get('name')) for track in album_details.get('tracks').get('items')]
	form = RateAlbumForm()
	form.best_track.choices = tracks
	if form.validate_on_submit():
		user = Users.query.filter_by(username=current_user.username).first_or_404()
		best_track = form.best_track.data
		overall = int(form.overall_rating.data)
		production = int(form.production_rating.data)
		unique = int(form.unique_rating.data)
		enjoyment = int(form.enjoyment_rating.data)
		thoughts = form.thoughts.data
		user_album_rating_update_or_add(user.username, album_id, best_track, overall, production, unique, enjoyment, thoughts)
		return redirect(url_for('.albums', username=current_user.username))
	return render_template('rate_album.html', form=form, name=name, link=link, art=art, artist=artist)


# TO DO
'''
Add functions to utilities to push things to the database
Add forms on the album details to rate the album and set favourite track
	Add database pushing to this
	Add a "thoughts" free text box
	Add different ratings
	Add listens (min(tracks.listens))
Add track details next to the tracks in the album details
	Add page to rate tracks
		Add database pushing to this
	Add number of listens
		Allow users to edit this, but take the recently played (update > last_run) and add the count to this
Add artist details
	Has list of albums
Add functions to delete ratings from albums/tracks
Add statistics to the homepage
Front page graphs? Some testing to see how matplotlib works
	static folder? With chart.pngs created on load?
		i.e. austinmh12_artistStats.png, Heil3_labelStats.png

'''