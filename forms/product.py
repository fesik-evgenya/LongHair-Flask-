from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, URL, Optional

class ProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    unit = StringField('Единица измерения', validators=[DataRequired()])
    purchase_price_without_vat = FloatField('Закупочная цена без НДС',
                                           validators=[DataRequired(), NumberRange(min=0)])
    vat_percent = FloatField('Процент НДС',
                            validators=[DataRequired(), NumberRange(min=0, max=100)])
    retail_price_without_vat = FloatField('Розничная цена без НДС',
                                         validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField('Ссылка на изображение', validators=[Optional(), URL()])
    supplier_id = IntegerField('ID поставщика', validators=[Optional()])
    supplier_name = StringField('Наименование поставщика', validators=[Optional()])
    supplier_type = StringField('Организационная форма', validators=[Optional()])
    submit = SubmitField('Добавить товар')