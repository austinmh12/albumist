import requests as r
import json
from base64 import b64encode
from psycopg2 import connect, ProgrammingError
import pandas as pd, numpy as np
from task_list.sql_queries import *
from flask import request
from datetime import datetime as dt
SPOTIFY_CLIENT_ID = '87a6082e432d47edb46dae2e29d3b6b5'
SPOTIFY_CLIENT_SECRET = 'd8582a4200734009ba26d4134e766520'
REDIRECT_URL = 'https://album-tracker.herokuapp.com/authorized'

###########
# SPOTIFY #
###########
def spotify_authorization():
	url = f'https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URL}&scope=user-read-private%20user-read-email%20user-read-recently-played'
	return url

def get_spotify_token(auth_code):
	url = 'https://accounts.spotify.com/api/token'
	header_auth = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'
	endcoded = b64encode(header_auth.encode()).decode()
	data = {
		'grant_type': 'authorization_code',
		'code': auth_code,
		'redirect_uri': REDIRECT_URL
	}
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'Authorization': f'Basic {endcoded}'
	}
	resp = r.post(url, headers=headers, data=data)
	return resp.json()

def refresh_spotify_token(refresh_token):
	url = 'https://accounts.spotify.com/api/token'
	header_auth = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'
	endcoded = b64encode(header_auth.encode()).decode()
	data = {
		'grant_type': 'refresh_token',
		'refresh_token': refresh_token
	}
	headers = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'Authorization': f'Basic {endcoded}'
	}
	resp = r.post(url, headers=headers, data=data)
	return resp.json()

def search_spotify(query, type, token):
	url = f'https://api.spotify.com/v1/search'
	params = {
		'q': query,
		'type': type
	}
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {token}'
	}
	return r.get(url, headers=headers, params=params).json()

def get_album_info(id, token):
	url = f'https://api.spotify.com/v1/albums/{id}'
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {token}'
	}
	return r.get(url, headers=headers).json()

def get_track_info(id, token):
	url = f'https://api.spotify.com/v1/tracks/{id}'
	headers = {
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {token}'
	}
	return r.get(url, headers=headers).json()

############
# DATABASE #
############
def sql(q, args):
	conn = connect(database='d81aremahv5dg1', host='ec2-3-230-106-126.compute-1.amazonaws.com', port='5432', user='zgbakvrmlxpmqq', password='b6726a650bf313755c5fa6089b09f5560900f36e9839b5d0721e47be96b342e2')
	conn.autocommit = True
	cur = conn.cursor()
	cur.execute(q, args)
	try:
		_df = pd.DataFrame.from_records(cur.fetchall(), columns=[desc[0] for desc in cur.description])
		conn.close()
		return _df
	except ProgrammingError:
		return None

######################
# USER ALBUM RATINGS #
######################
def get_user_album_rating(user, album_id):
	df = sql(GET_USER_ALBUM_RATING, (user, album_id))
	if df.empty:
		return None
	return int(df.user_album_rating_id[0])

def add_user_album_rating(user, album_spotify_id, best_track, overall, production, unique, enjoyment, thoughts):
	album_id = get_album_id_from_spotify_id(album_spotify_id)
	if not album_id:
		album_id = add_album(album_spotify_id)
	user_id = get_user_id_from_username(user)
	track_id = get_track_id_from_track_spotify_id(best_track)
	if not track_id:
		track_id = add_track(album_spotify_id, best_track)
	sql(ADD_USER_ALBUM_RATING, (user_id, album_id, track_id, overall, production, unique, enjoyment, thoughts))

def update_user_album_rating(user, album_id, track, overall, production, unique, enjoyment, thoughts):
	user_id = get_user_id_from_username(user)
	track_id = get_track_id_from_track_spotify_id(track)
	if not track_id:
		track_id = add_track(album_id, track)
	sql(UPDATE_USER_ALBUM_RATING, (track_id, overall, production, unique, enjoyment, thoughts, user_id, album_id))

def user_album_rating_update_or_add(user, album_spotify_id, best_track, overall, production, unique, enjoyment, thoughts):
	user_id = get_user_id_from_username(user)
	album_id = get_album_id_from_spotify_id(album_spotify_id)
	if not album_id:
		album_id = add_album(album_spotify_id)
	uar_id = get_user_album_rating(user_id, album_id)
	if uar_id:
		update_user_album_rating(user, album_id, best_track, overall, production, unique, enjoyment, thoughts)
	else:
		add_user_album_rating(user, album_spotify_id, best_track, overall, production, unique, enjoyment, thoughts)


##########
# ALBUMS #
##########
def get_album_id_from_spotify_id(album_spotify_id):
	df = sql(GET_ALBUM, (album_spotify_id,))
	if df.empty:
		return None
	return int(df.album_id[0])

def add_album(album_spotify_id):
	token = request.cookies.get('spotifyToken')
	album_info = get_album_info(album_spotify_id, token)
	artist_id = get_artist_id(album_info.get('artists')[0].get('id'))
	if not artist_id:
		artist_id = add_artist(album_info.get('artists')[0].get('name'), album_info.get('artists')[0].get('id'))
	album_name = album_info.get('name')
	album_art = album_info.get('images')[0].get('url')
	label_id = get_label_id(album_info.get('label'))
	if not label_id:
		label_id = add_label(album_info.get('label'))
	release_date = album_info.get('release_date')
	genres = album_info.get('genres')
	if not genres:
		genres = ''
	album_url = album_info.get('external_urls').get('spotify')
	sql(ADD_ALBUM, (album_spotify_id,artist_id,album_name,album_url,album_art,label_id,release_date,genres))


#########
# USERS #
#########
def get_user_id_from_username(username):
	df = sql(GET_USER, (username,))
	if df.empty:
		return None
	return int(df.user_id[0])

def add_user(username, email, password):
	pass

def edit_user(email, password, last_login):
	pass

def remove_user(username):
	pass

###########
# ARTISTS #
###########
def get_artist_id(artist_spotify_id):
	df = sql(GET_ARTIST, (artist_spotify_id,))
	if df.empty:
		return None
	return int(df.artist_id[0])

def add_artist(name, artist_spotify_id):
	sql(ADD_ARTIST, (artist_spotify_id, name))
	return get_artist_id(artist_spotify_id)


##########
# TRACKS #
##########
def add_track(album_spotify_id, best_track):
	token = request.cookies.get('spotifyToken')
	album_info = get_album_info(album_spotify_id, token)
	artist_id = get_artist_id(album_info.get('artists')[0].get('id'))
	if not artist_id:
		artist_id = add_artist(album_info.get('artists')[0].get('name'), album_info.get('artists')[0].get('id'))
	album_id = get_album_id_from_spotify_id(album_spotify_id)
	if not album_id:
		album_id = add_album(album_spotify_id)
	track_info = get_track_info(best_track, token)
	track_id = track_info.get('id')
	track_number = track_info.get('track_number')
	duration = track_info.get('duration_ms')
	name = track_info.get('name')
	track_url = track_info.get('external_urls').get('spotify')
	producer_id = None # FIX THIS ONCE GENIUS IS IMPLEMENTED
	lyrics = None # FIX THIS ONCE GENIUS IS IMPLEMENTED
	sql(ADD_TRACK, (track_id,artist_id,album_id,track_number,name,duration,producer_id,track_url,lyrics))
	return get_track_id_from_track_spotify_id(track_id)

def get_track_id_from_track_spotify_id(track):
	df = sql(GET_TRACK, (track,))
	if df.empty:
		return None
	return int(df.track_id[0])


##########
# LABELS #
##########
def get_label_id(name):
	df = sql(GET_LABEL, (name,))
	if df.empty:
		return None
	return int(df.label_id[0])

def add_label(name):
	sql(ADD_LABEL, (name,))
	return get_label_id(name)