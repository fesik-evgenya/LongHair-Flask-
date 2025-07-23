from data.db_session import global_init, create_session
from data.loyalty import LoyaltyLevel


def init_loyalty():
    global_init('db/shop.db')
    db_sess = create_session()

    levels = [
        {'id': 1, 'level_name': 'Базовый', 'discount': 0.0, 'min_purchases': 0, 'min_total': 0},
        {'id': 2, 'level_name': 'Серебряный', 'discount': 5.0, 'min_purchases': 5, 'min_total': 10000},
        {'id': 3, 'level_name': 'Золотой', 'discount': 10.0, 'min_purchases': 15, 'min_total': 50000},
        {'id': 4, 'level_name': 'Администратор', 'discount': 0.0, 'min_purchases': 0, 'min_total': 0},
        {'id': 5, 'level_name': 'Prime', 'discount': 0, 'min_purchases': 0, 'min_total': 0}
    ]

    for level in levels:
        if not db_sess.query(LoyaltyLevel).get(level['id']):
            new_level = LoyaltyLevel(**level)
            db_sess.add(new_level)

    db_sess.commit()


if __name__ == '__main__':
    init_loyalty()