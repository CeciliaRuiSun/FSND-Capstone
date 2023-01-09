from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, ValidationError
from wtforms.widgets import PasswordInput

def password_validator(form, field):
        # Check that the password contains at least one uppercase letter, one lowercase letter, and one number
        if not any(char.isdigit() for char in field.data):
            raise ValidationError('Password must contain at least one number')

        if not any(char.isupper() for char in field.data):
            raise ValidationError('Password must contain at least one uppercase letter')

        if not any(char.islower() for char in field.data):
            raise ValidationError('Password must contain at least one lowercase letter')

class UserForm(Form):
    
    username = StringField(
        'username', validators=[DataRequired()]
    )

    email = StringField(
        'email', validators=[DataRequired()]
    )

    password = PasswordField(
        'password', validators=[InputRequired(), Length(min=8, message='Too short'), password_validator]
        )

    confirm = PasswordField(
        'confirm', validators=[InputRequired(), EqualTo('password', 'Password mismatch'), password_validator]
        )

    phone_number = StringField(
        'phone_number'
    )

    connection = StringField(
        'connection', validators=[DataRequired()]
    )

