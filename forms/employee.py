from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class EmployeeForm(FlaskForm):
    surname = StringField('Фамилия сотрудника', validators=[DataRequired()])
    primary_name = StringField('Имя сотрудника', validators=[DataRequired()])
    secondary_name = StringField('Отчество сотрудника', validators=[DataRequired()])
    position = SelectField('Должность', choices=[
        ('сборщик', 'Сборщик заказов'),
        ('курьер', 'Курьер'),
        ('менеджер', 'Менеджер'),
        ('администратор', 'Администратор')
    ], validators=[DataRequired()])
    email = StringField('Рабочий email', validators=[DataRequired(), Email()])
    phone = StringField('Рабочий телефон', validators=[DataRequired()])
    status = SelectField('Статус', choices=[
        (1, 'Активен'),
        (0, 'Неактивен')
    ], coerce=int, default=1)
    submit = SubmitField('Сохранить')