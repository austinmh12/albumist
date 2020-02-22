# USER ALBUM RATINGS
GET_USER_ALBUM_RATING = '''
SELECT
	*
FROM
	user_album_ratings
WHERE
	user_id = %s
	and album_id = %s
LIMIT 1
'''

ADD_USER_ALBUM_RATING = '''
INSERT INTO user_album_ratings
	(user_id, album_id, best_track_id, overall_rating, production_rating, unique_rating, enjoyment_rating, thoughts)
VALUES
	(%s,%s,%s,%s,%s,%s,%s,%s)
'''

UPDATE_USER_ALBUM_RATING = '''
UPDATE user_album_ratings
SET best_track_id = %s,
	overall_rating = %s,
	production_rating = %s,
	unique_rating = %s,
	enjoyment_rating = %s,
	thoughts = %s
WHERE
	user_id = %s
	and album_id = %s
'''

# ALBUMS
GET_ALBUM = '''
SELECT
	*
FROM
	albums
WHERE
	album_spotify_id = %s
LIMIT 1
'''

ADD_ALBUM = '''
INSERT INTO albums
	(album_spotify_id,artist_id,album_name,album_url,art_url,label_id,release_year,genre)
VALUES
	(%s,%s,%s,%s,%s,%s,%s,%s)
'''

# USERS
GET_USER = '''
SELECT
	*
FROM
	users
WHERE
	username = %s
LIMIT 1
'''

# ARTISTS
GET_ARTIST = '''
SELECT
	*
FROM
	artists
WHERE
	artist_spotify_id = %s
LIMIT 1
'''

ADD_ARTIST = '''
INSERT INTO artists
	(artist_spotify_id, artist_name)
VALUES
	(%s,%s)
'''

# LABELS
GET_LABEL = '''
SELECT
	*
FROM
	labels
WHERE
	label_name = %s
LIMIT 1
'''

ADD_LABEL = '''
INSERT INTO labels
	(label_name)
VALUES
	(%s)
'''

# TRACKS
GET_TRACK = '''
SELECT
	*
FROM
	tracks
WHERE
	track_spotify_id = %s
LIMIT 1
'''

ADD_TRACK = '''
INSERT INTO tracks
	(track_spotify_id,artist_id,album_id,track_number,track_name,duration_ms,producer_id,track_url,lyrics_url)
VALUES
	(%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''