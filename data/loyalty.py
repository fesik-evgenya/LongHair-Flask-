import sqlalchemy
from .db_session import SqlAlchemyBase


class LoyaltyLevel(SqlAlchemyBase):
    __tablename__ = 'loyalty_levels'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    level_name = sqlalchemy.Column(sqlalchemy.String, nullable=False) # статус
    discount = sqlalchemy.Column(sqlalchemy.Float, nullable=False)  # скидка в процентах
    min_purchases = sqlalchemy.Column(sqlalchemy.Integer, default=0)  # минимальное количество покупок для уровня
    min_total = sqlalchemy.Column(sqlalchemy.Float, default=0)  # минимальная сумма покупок для уровня