import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase

class Customer(SqlAlchemyBase, UserMixin):
    __tablename__ = 'customers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)  # емеил
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # имя
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # номер телефона
    street = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # улица
    building = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # дом
    entrance = sqlalchemy.Column(sqlalchemy.String, default='-')  # парадная
    floor = sqlalchemy.Column(sqlalchemy.String, default='-')  # этаж
    apartment = sqlalchemy.Column(sqlalchemy.String, default='-')  # квартира
    loyalty_level = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('loyalty_levels.id'),
                                      default=1)  # связь с уровнем лояльности
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # статус клиента
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # дата регистрации клиента
    # связь с таблицей заказов
    orders = orm.relationship("Order", back_populates='user')  # связь с таблицей заказов
    loyalty = orm.relationship("LoyaltyLevel")  # связь с таблицей уровней лояльности

    # кодируем пароль пользователя и отправляем в переменную
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # сверяем пароль с зашифрованным паролем пользователем
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
