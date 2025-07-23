from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class EditProfileForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Телефон', validators=[DataRequired()])
    street = StringField('Улица', validators=[DataRequired()])
    building = StringField('Дом', validators=[DataRequired()])
    entrance = StringField('Парадная (необязательно)')
    floor = StringField('Этаж (необязательно)')
    apartment = StringField('Квартира (необязательно)')
    submit = SubmitField('Сохранить изменения')