import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)  # наименование
    unit = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # единица измерения
    purchase_price_without_vat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # закупочная цена без НДС
    vat_percent = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # процент НДС
    vat_amount = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # сумма НДС
    purchase_price_with_vat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # закупочная цена с НДС
    retail_price_without_vat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # розничная цена без НДС
    retail_vat_amount = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # НДС розничная
    retail_price_with_vat = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # розничная цена с НДС
    image_url = sqlalchemy.Column(sqlalchemy.String)  # ссылка на изображение
    supplier_id = sqlalchemy.Column(sqlalchemy.Integer)  # ID поставщика
    supplier_name = sqlalchemy.Column(sqlalchemy.String)  # наименование поставщика
    supplier_type = sqlalchemy.Column(sqlalchemy.String)  # организационная форма

    # связь с заказами
    orders = orm.relationship("Order", back_populates="product")