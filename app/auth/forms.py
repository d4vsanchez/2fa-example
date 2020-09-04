from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')


class Enable2FAForm(FlaskForm):
    submit = SubmitField('Enable 2FA')


class Disable2FAForm(FlaskForm):
    submit = SubmitField('Disable 2FA')


class Check2FAForm(FlaskForm):
    token = StringField('Received token', validators=[Length(min=1, max=7), DataRequired()])
    submit = SubmitField('Check')
