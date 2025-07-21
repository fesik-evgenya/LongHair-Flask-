from flask import Flask, url_for, request, render_template, redirect, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os.path
import sqlite3
from sqlite3 import Error

from data import db_session

from forms.loginform import LoginForm
from data.customers import Customer # Импорт модели клиентов
from data.orders import Order  # Импорт модели заказов
from data.products import Product  # Импорт модели продуктов
from data.loyalty import LoyaltyLevel  # Импорт модели уровней лояльности
from forms.user import Register
from forms.product import ProductForm

# Регистрируем приложение Flask
app = Flask(__name__)

# Секретный ключ для сессий и защиты от CSRF
app.secret_key = 'Tdutif_85'

# Разрешенные расширения для загрузки файлов
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'zip', 'jpg', 'png']
debug = True  # Режим отладки (True для разработки, False для продакшена)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Страница для входа


# Загрузчик пользователей для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(Customer, user_id)  # Загружаем пользователя из БД по ID


# Обработчик ошибки 404 (страница не найдена)
@app.errorhandler(404)
def not_found(y):
    return render_template('404.html', title="Не найдено")


# Главная страница
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', title="Район {Фруктовый}")


# Страница "О нас"
@app.route('/about')
def about():
    return render_template('about.html', title="Район {Фруктовый} | О нас")


# Страница товаров
@app.route('/goods')
def goods():
    return render_template('goods.html', title="Район {Фруктовый} | Товары")


# Страница контактов
@app.route('/contacts')
def contacts():
    # Параметры для передачи в шаблон
    params = dict()
    params['phone'] = '+7 (999) 999-99-99'
    params['email'] = 'info@rayon-fruktovy.ru'
    params['address'] = 'г. Санкт-Петербург, Среднерогатская ул. д.12к1'
    params['vk_group'] = 'https://vk.com/rayon-fruktovy'
    params['telegram'] = '#'
    params['whatsapp'] = '#'
    params['map_coords'] = [59.824518, 30.337296]
    params['logo_path'] = url_for('static', filename='images/logo/favicon.svg')

    return render_template(
        'contacts.html', title="Район {Фруктовый} | Контакты", **params)


# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # Поиск пользователя по email
        user = db_sess.query(Customer).filter(Customer.email == form.email.data).first()

        # Проверка пароля
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')  # Перенаправление на главную после входа
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Район {Фруктовый} | Авторизация', form=form)


# Выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')  # Перенаправление на главную после выхода


# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        # Проверка совпадения паролей
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Район {Фруктовый} | Регистрация',
                                   form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()

        # Проверка уникальности email
        if db_sess.query(Customer).filter(Customer.email == form.email.data).first():
            return render_template('register.html', title='Район {Фруктовый} | Регистрация',
                                   form=form, message="Пользователь с такой почтой уже есть")

        # Проверка уникальности телефона
        if db_sess.query(Customer).filter(Customer.phone == form.phone.data).first():
            return render_template('register.html', title='Район {Фруктовый} | Регистрация',
                                   form=form, message="Пользователь с таким телефоном уже есть")

        # Создание нового пользователя
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            street=form.street.data,
            building=form.building.data,
            entrance=form.entrance.data or '-',
            floor=form.floor.data or '-',
            apartment=form.apartment.data or '-',
            status=0  # Статус по умолчанию: базовый (0)
        )
        customer.set_password(form.password.data)  # Хеширование пароля

        db_sess.add(customer)
        db_sess.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect('/login')  # Перенаправление на страницу входа

    return render_template('register.html', title='Район {Фруктовый} | Регистрация', form=form)


# Страница профиля (только для авторизованных пользователей)
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Район {Фруктовый} | Ваш профиль', user=current_user)


# Страница заказов пользователя
@app.route('/orders')
@login_required
def user_orders():
    db_sess = db_session.create_session()
    # Получаем все заказы текущего пользователя
    orders = db_sess.query(Order).filter(Order.user_id == current_user.id).all()
    return render_template('orders.html', title='Район {Фруктовый} | Ваши заказы', orders=orders)


# Панель администратора (только для админов)
@app.route('/admin')
@login_required
def admin_panel():
    # Проверка прав администратора (status=3)
    if current_user.status != 3:
        flash('Доступ запрещен: недостаточно прав', 'danger')
        return redirect('/')

    db_sess = db_session.create_session()

    # Получаем данные для панели администратора
    users = db_sess.query(Customer).all()
    orders = db_sess.query(Order).all()
    products = db_sess.query(Product).all()

    return render_template('admin_panel.html',
                           title='Панель администратора',
                           users=users,
                           orders=orders,
                           products=products)

# Страница добавления товара в базу (только для админов)
@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.status != 3:
        flash('Доступ запрещен: недостаточно прав', 'danger')
        return redirect('/')

    form = ProductForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        # рассчитываем производные поля
        vat_amount = form.purchase_price_without_vat.data * (form.vat_percent.data / 100)
        purchase_price_with_vat = form.purchase_price_without_vat.data + vat_amount

        retail_vat_amount = form.retail_price_without_vat.data * (form.vat_percent.data / 100)
        retail_price_with_vat = form.retail_price_without_vat.data + retail_vat_amount

        product = Product(
            name=form.name.data,
            unit=form.unit.data,
            purchase_price_without_vat=form.purchase_price_without_vat.data,
            vat_percent=form.vat_percent.data,
            vat_amount=vat_amount,
            purchase_price_with_vat=purchase_price_with_vat,
            retail_price_without_vat=form.retail_price_without_vat.data,
            retail_vat_amount=retail_vat_amount,
            retail_price_with_vat=retail_price_with_vat,
            image_url=form.image_url.data,
            supplier_id=form.supplier_id.data,
            supplier_name=form.supplier_name.data,
            supplier_type=form.supplier_type.data
        )

        db_sess.add(product)
        db_sess.commit()

        flash('Товар успешно добавлен!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('add_product.html', title='Район {Фруктовый} | Добавить товар', form=form)

# Главная функция запуска приложения
if __name__ == '__main__':
    # Инициализация базы данных
    db_session.global_init('db/shop.db')  # Путь к файлу базы данных

    # # Создаем сессию для работы с БД
    # db_sess = db_session.create_session()
    #
    # # Проверяем и создаем начальные данные, если их нет
    # # Создаем уровни лояльности, если их нет
    # if not db_sess.query(LoyaltyLevel).first():
    #     levels = [
    #         LoyaltyLevel(id=0, level_name="Базовый", discount=0.0),
    #         LoyaltyLevel(id=1, level_name="Серебряный", discount=5.0),
    #         LoyaltyLevel(id=2, level_name="Золотой", discount=10.0),
    #         LoyaltyLevel(id=3, level_name="Администратор", discount=0.0)
    #     ]
    #     db_sess.add_all(levels)
    #     db_sess.commit()
    #
    # # Создаем администратора, если его нет
    # if not db_sess.query(Customer).filter(Customer.email == 'ganef85@mail.ru').first():
    #     admin = Customer(
    #         name="Администратор",
    #         email="ganef85@mail.ru",
    #         phone="+7(950)012-40-11",
    #         street="Административная",
    #         building="1",
    #         entrance='-',
    #         floor='-',
    #         apartment='-',
    #         status=3  # статус администратора
    #     )
    #     admin.set_password("Tdutif_85")
    #     db_sess.add(admin)
    #     db_sess.commit()

    # Запуск приложения
    app.run(host='localhost', port=5000, debug=debug)