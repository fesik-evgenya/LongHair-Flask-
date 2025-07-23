from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired, NumberRange, URL, Optional
from flask_wtf.file import FileAllowed

class ProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    category = SelectField('Категория товара',
                         choices=[
                             ('овощи', 'Овощи'),
                             ('фрукты', 'Фрукты'),
                             ('ягоды', 'Ягоды'),
                             ('сухофрукты', 'Сухофрукты'),
                             ('орехи', 'Орехи'),
                             ('зелень', 'Зелень'),
                             ('грибы', 'Грибы')
                         ],
                         validators=[DataRequired()])
    unit = StringField('Единица измерения', validators=[DataRequired()])
    purchase_price_without_vat = FloatField('Закупочная цена без НДС',
                                           validators=[DataRequired(), NumberRange(min=0)])
    vat_percent = FloatField('Процент НДС',
                            validators=[DataRequired(), NumberRange(min=0, max=100)])
    retail_price_without_vat = FloatField('Розничная цена без НДС',
                                         validators=[DataRequired(), NumberRange(min=0)])
    description = TextAreaField('Описание товара', validators=[DataRequired()])
    image = FileField('Изображение товара',
                     validators=[FileAllowed(['webp'], 'Только WebP изображения!')])
    supplier_id = IntegerField('ID поставщика', validators=[Optional()])
    supplier_name = StringField('Наименование поставщика', validators=[Optional()])
    supplier_type = StringField('Организационная форма', validators=[Optional()])
    submit = SubmitField('Добавить товар')