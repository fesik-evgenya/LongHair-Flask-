import sqlalchemy
from sqlalchemy import orm
import datetime
from .db_session import SqlAlchemyBase


class Employee(SqlAlchemyBase):
    __tablename__ = 'employees'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # Фамилия сотрудника
    primary_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # Имя сотрудника
    secondary_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Отчество сотрудника
    position = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # Должность
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)  # Рабочий email
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # Рабочий телефон
    hire_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # Дата приема
    status = sqlalchemy.Column(sqlalchemy.Integer, default=1)  # 1-активен, 0-неактивен
    termination_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)  # Дата увольнения

    # Связь с заказами
    assembled_orders = orm.relationship("Order", foreign_keys="Order.assembler_id", back_populates="assembler")
    delivered_orders = orm.relationship("Order", foreign_keys="Order.courier_id", back_populates="courier")