import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    # Константы статусов
    STATUS_NEW = 'новый'
    STATUS_PROCESSING = 'в обработке'
    STATUS_DELIVERY = 'доставляется'
    STATUS_COMPLETED = 'завершен'
    STATUS_CANCELLED = 'аннулирован'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('customers.id'))
    # номенклатура товара, тянем из таблицы products
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'), nullable=False)
    unit = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # единица измерения
    price_per_unit = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # цена за единицу
    quantity = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # количество
    total_price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # общая стоимость
    discount = sqlalchemy.Column(sqlalchemy.Float, default=0.0)  # скидка
    discounted_price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # цена со скидкой
    tax = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # Налог (18%)
    order_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    order_number = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)  # номер заказа
    status = sqlalchemy.Column(sqlalchemy.String, default='создан')  # статус заказа
    assembler_id = sqlalchemy.Column(sqlalchemy.Integer)  # ID сборщика
    courier_id = sqlalchemy.Column(sqlalchemy.Integer)  # ID курьера

    user = orm.relationship('Customer', back_populates='orders') # Связь с пользователем
    product = orm.relationship('Product', back_populates='orders')  # Связь с продуктом


class CartItem(SqlAlchemyBase):
    __tablename__ = 'cart_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('customers.id'), nullable=False)
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id'), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Float, default=0.5)  # Шаг 0.5 кг

    user = orm.relationship('Customer')
    product = orm.relationship('Product')
