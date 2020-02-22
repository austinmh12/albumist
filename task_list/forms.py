from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class SearchForm(FlaskForm):
	album_name = StringField('Album', validators=[DataRequired()])
	artist_name = StringField('Artist')
	type = StringField('Type')
	search = SubmitField('Search')

class RateAlbumForm(FlaskForm):
	best_track = SelectField('Best Track')
	overall_rating = SelectField('Overall',
		choices=[(str(i+1), i+1) for i in range(0,10)],
		validators=[DataRequired()])
	production_rating = SelectField('Production Value',
		choices=[(str(i+1), i+1) for i in range(0,10)])
	unique_rating = SelectField('Uniqueness',
		choices=[(str(i+1), i+1) for i in range(0,10)])
	enjoyment_rating = SelectField('Enjoyment',
		choices=[(str(i+1), i+1) for i in range(0,10)])
	thoughts = TextAreaField('Thoughts')
	rate = SubmitField('Rate')