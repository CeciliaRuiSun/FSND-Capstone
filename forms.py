from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL

class UserForm(Form):
    
    username = StringField(
        'username', validators=[DataRequired()]
    )

    family_name = StringField(
        'family_name'
    )

    give_name = StringField(
        'given_name'
    )

    email = StringField(
        'email', validators=[DataRequired()]
    )

    phone_number = StringField(
        'phone_number'
    )

    connection = StringField(
        'connection', validators=[DataRequired()]
    )

