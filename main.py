import os
from flask import Flask, url_for, request, render_template, redirect, flash, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect, validate_csrf, CSRFError
import datetime
from math import ceil
from werkzeug.utils import secure_filename

# Импорты моделей и форм
from data.customers import Customer
from data.orders import Order, CartItem
from data.products import Product
from forms.loginform import LoginForm
from forms.product import ProductForm
from forms.user import Register
from forms.editprofile import EditProfileForm
from data.employees import Employee
from forms.employee import EmployeeForm
from notifications.send_mail import send_mail

# Регистрируем приложение Flask
app = Flask(__name__)

# Конфигурация подключения к PostgreSQL на Render
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql://shop_admin:m74Tk1oMkdcAAHMdWDAvjwEA2yRDbY89@dpg-d24aac1r0fns73b02n7g-a/shop_qpjp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Секретный ключ для сессий и защиты от CSRF
app.secret_key = 'Tdutif_85'
csrf = CSRFProtect(app)

# конфигурации
app.config['UPLOAD_FOLDER'] = 'static/images/goods'
app.config['ALLOWED_EXTENSIONS'] = {'webp'}
debug = True  # Режим отладки (True для разработки, False для продакшена)

# проверяем загружаемый файл на расширение
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Страница для входа

# Ограничение: 50 запросов в минуту с одного IP
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Автоматически определяет IP
    default_limits=["50 per minute"]
)

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
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Количество товаров на странице

    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    db_sess = db_session.create_session()
    query = db_sess.query(Product)

    # Применяем фильтры
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    if category_filter:
        query = query.filter(Product.category == category_filter)

    # Ручная реализация пагинации
    total_items = query.count()
    total_pages = ceil(total_items / per_page) if total_items > 0 else 1
    offset = (page - 1) * per_page
    items = query.offset(offset).limit(per_page).all()

    # Создаем объект пагинации для шаблона
    class Pagination:
        def __init__(self, page, per_page, total_items, items, total_pages):
            self.page = page
            self.per_page = per_page
            self.total = total_items
            self.items = items
            self.pages = total_pages

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None

        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None

        def iter_pages(self, left_edge=1, right_edge=1, left_current=1, right_current=2):
            if self.pages == 0:
                return []

            left_start = 1
            left_end = min(left_edge, self.pages)

            right_start = max(self.pages - right_edge + 1, 1)
            right_end = self.pages

            current_start = max(self.page - left_current, 1)
            current_end = min(self.page + right_current, self.pages)

            pages = set()
            # Добавляем левый блок
            pages.update(range(left_start, left_end + 1))
            # Добавляем правый блок
            pages.update(range(right_start, right_end + 1))
            # Добавляем текущий блок
            pages.update(range(current_start, current_end + 1))

            sorted_pages = sorted(pages)
            prev_page = 0
            for page_num in sorted_pages:
                if page_num - prev_page > 1:
                    yield None  # Генератор для многоточия
                yield page_num
                prev_page = page_num

    products = Pagination(page, per_page, total_items, items, total_pages)

    return render_template(
        'goods.html',
        title="Район {Фруктовый} | Товары",
        products=products
    )


# API для получения количества товаров в корзине
@app.route('/api/cart_count')
@login_required
def cart_count():
    db_sess = db_session.create_session()
    count = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).count()
    return jsonify({'count': count})


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
@limiter.limit("20 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # Поиск пользователя по email
        user = db_sess.query(Customer).filter(Customer.email == form.email.data).first()

        # Проверка пароля
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            # # Перенаправляем администраторов в админ-панель
            # if user.status in [4, 5]:
            #     return redirect(url_for('admin_panel'))

            # Всех пользователей перенаправляем в профиль
            return redirect(url_for('profile'))

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
@limiter.limit("5 per minute")
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
    # Проверка прав администратора (status=4 или 5)
    if current_user.status not in [4, 5]:
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


# Страница добавления товара в базу (только для prime-админов (5 lvl)
@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    # проверяем статус 5 (только для prime-администраторов)
    if current_user.status != 5:
        flash('Доступ запрещен: недостаточно прав', 'danger')
        return redirect('/')

    form = ProductForm()

    if form.validate_on_submit():
        try:
            db_sess = db_session.create_session()

            # Обработка загрузки изображения
            image_url = None
            if form.image.data:
                file = form.image.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_path = app.config['UPLOAD_FOLDER']

                    # Создаем папку если не существует
                    os.makedirs(upload_path, exist_ok=True)

                    # Сохраняем файл
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)

                    # Формируем относительный путь для БД
                    image_url = f'static/images/goods/{filename}'

            # Расчеты цен
            vat_amount = form.purchase_price_without_vat.data * (form.vat_percent.data / 100)
            purchase_price_with_vat = form.purchase_price_without_vat.data + vat_amount

            retail_vat_amount = form.retail_price_without_vat.data * (form.vat_percent.data / 100)
            retail_price_with_vat = form.retail_price_without_vat.data + retail_vat_amount

            # Создание товара
            product = Product(
                name=form.name.data,
                unit=form.unit.data,
                category=form.category.data,
                purchase_price_without_vat=form.purchase_price_without_vat.data,
                vat_percent=form.vat_percent.data,
                vat_amount=vat_amount,
                purchase_price_with_vat=purchase_price_with_vat,
                retail_price_without_vat=form.retail_price_without_vat.data,
                retail_vat_amount=retail_vat_amount,
                retail_price_with_vat=retail_price_with_vat,
                image_url=image_url,
                description=form.description.data,
                supplier_id=form.supplier_id.data,
                supplier_name=form.supplier_name.data,
                supplier_type=form.supplier_type.data
            )

            db_sess.add(product)
            db_sess.commit()

            flash('Товар успешно добавлен!', 'success')
            return redirect(url_for('admin_panel'))

        except Exception as e:
            flash(f'Ошибка при добавлении товара: {str(e)}', 'danger')

    # Показываем ошибки валидации
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле "{getattr(form, field).label.text}": {error}', 'danger')

    return render_template('add_product.html', title='Добавить товар', form=form)


@app.route('/admin/employees')
@login_required
def list_employees():
    if current_user.status != 5:
        flash('Доступ запрещен', 'danger')
        return redirect('/')

    db_sess = db_session.create_session()
    employees = db_sess.query(Employee).all()
    return render_template('employees.html',
                           title='Управление сотрудниками',
                           employees=employees)


# Добавление сотрудника
@app.route('/admin/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if current_user.status != 5:
        flash('Доступ запрещен', 'danger')
        return redirect('/')

    form = EmployeeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        employee = Employee(
            name=form.name.data,
            position=form.position.data,
            email=form.email.data,
            phone=form.phone.data,
            status=form.status.data
        )
        db_sess.add(employee)
        db_sess.commit()
        flash('Сотрудник добавлен', 'success')
        return redirect(url_for('list_employees'))
    return render_template('add_employee.html',
                           title='Добавить сотрудника',
                           form=form)


# Редактирование сотрудника (только для Prime - админа(5 lvl))
@app.route('/admin/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    if current_user.status != 5:
        flash('Доступ запрещен', 'danger')
        return redirect('/')

    db_sess = db_session.create_session()
    employee = db_sess.query(Employee).get(id)

    if not employee:
        flash('Сотрудник не найден', 'danger')
        return redirect(url_for('list_employees'))

    form = EmployeeForm(obj=employee)
    if form.validate_on_submit():
        employee.name = form.name.data
        employee.position = form.position.data
        employee.email = form.email.data
        employee.phone = form.phone.data
        employee.status = form.status.data
        db_sess.commit()
        flash('Изменения сохранены', 'success')
        return redirect(url_for('list_employees'))
    return render_template('edit_employee.html',
                           title='Редактировать сотрудника',
                           form=form,
                           employee=employee)


# Редактирование сотрудника (только для Prime - админа(5 lvl))
# Удаление сотрудника
@app.route('/admin/employees/delete/<int:id>', methods=['POST'])
@login_required
def delete_employee(id):
    if current_user.status != 5:
        flash('Доступ запрещен', 'danger')
        return redirect('/')

    db_sess = db_session.create_session()
    employee = db_sess.query(Employee).get(id)

    if employee:
        db_sess.delete(employee)
        db_sess.commit()
        flash('Сотрудник удален', 'success')
    return redirect(url_for('list_employees'))


# отправляем с сайта(раздел контакты) письмо на центральную корп. почту
@app.route('/send_contact_form', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def send_contact_form():
    if request.method == 'GET':
        return jsonify({"error": "Method not allowed"}), 405
    try:
        # Получаем JSON данные
        data = request.get_json()

        # Проверяем обязательные поля
        required_fields = ['name', 'email', 'subject', 'message', 'csrf_token']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": "Все поля обязательны для заполнения"
            }), 400

        # Валидация email
        if '@' not in data['email'] or '.' not in data['email'].split('@')[1]:
            return jsonify({
                "success": False,
                "message": "Введите корректный email"
            }), 400

        # Отправка письма
        email_body = f"""
        Имя: {data['name']}
        Email: {data['email']}
        Тема: {data['subject']}
        Сообщение:
        {data['message']}
        """

        if send_mail(
                to_email="ganef85@mail.ru",
                subject=f"Новое сообщение: {data['subject']}",
                message=email_body
        ):
            return jsonify({
                "success": True,
                "message": "Ваше сообщение успешно отправлено!"
            })

    except Exception as e:
        print(f"Ошибка при обработке формы: {str(e)}")

    return jsonify({
        "success": False,
        "message": "Произошла ошибка на сервере"
    }), 500


# функция-фильтр для преобразования статуса заказа в класс CSS
def status_to_badge_class(status):
    status = status.lower()
    if status in ['новый', 'создан']:
        return 'bg-primary'
    elif status == 'в обработке':
        return 'bg-info'
    elif status == 'доставляется':
        return 'bg-warning'
    elif status == 'завершен':
        return 'bg-success'
    elif status == 'аннулирован':
        return 'bg-secondary'
    else:
        return 'bg-light text-dark'


# регистрируем фильтр в Jinja2
app.jinja_env.filters['status_badge_class'] = status_to_badge_class


# Маршрут для активных заказов (только для администраторов)
@app.route('/active-orders')
@login_required
def active_orders():
    # Проверка прав администратора (status=3)
    if current_user.status not in [4, 5]:
        flash('Доступ запрещен: недостаточно прав', 'danger')
        return redirect('/')

    db_sess = db_session.create_session()
    # Фильтрация активных заказов (исключаем завершенные и аннулированные)
    orders = db_sess.query(Order).filter(
        ~Order.status.in_(['завершен', 'аннулирован'])
    ).all()

    return render_template('active_orders.html',
                           title='Активные заказы',
                           orders=orders)


# пользователь сам меняет в базе личные данные из своего профиля
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Customer).get(current_user.id)

        # Проверка уникальности email (если изменился)
        if user.email != form.email.data:
            if db_sess.query(Customer).filter(Customer.email == form.email.data).first():
                flash('Пользователь с такой почтой уже существует', 'danger')
                return render_template('edit_profile.html', title='Редактирование профиля', form=form)

        # Проверка уникальности телефона (если изменился)
        if user.phone != form.phone.data:
            if db_sess.query(Customer).filter(Customer.phone == form.phone.data).first():
                flash('Пользователь с таким телефоном уже существует', 'danger')
                return render_template('edit_profile.html', title='Редактирование профиля', form=form)

        # Обновление данных
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.street = form.street.data
        user.building = form.building.data
        user.entrance = form.entrance.data or '-'
        user.floor = form.floor.data or '-'
        user.apartment = form.apartment.data or '-'

        db_sess.commit()
        flash('Профиль успешно обновлен!', 'success')
        return redirect(url_for('profile'))

    # Заполнение формы текущими данными
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.street.data = current_user.street
        form.building.data = current_user.building
        form.entrance.data = current_user.entrance if current_user.entrance != '-' else ''
        form.floor.data = current_user.floor if current_user.floor != '-' else ''
        form.apartment.data = current_user.apartment if current_user.apartment != '-' else ''

    return render_template('edit_profile.html', title='Редактирование профиля', form=form)


# Добавление товара в корзину
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        # Проверяем CSRF из заголовка
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token:
            return jsonify({
                'success': False,
                'message': 'Отсутствует CSRF токен'
            }), 400

        validate_csrf(csrf_token)

    except CSRFError as e:
        app.logger.error(f"CSRF validation failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Недействительный CSRF токен'
        }), 400

    db_sess = db_session.create_session()
    # Проверяем есть ли уже товар в корзине
    cart_item = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == product_id
    ).first()

    if cart_item:
        cart_item.quantity += 0.5
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=0.5
        )
        db_sess.add(cart_item)

    db_sess.commit()

    # Получаем обновленное количество товаров в корзине
    cart_count = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).count()

    return jsonify({
        'success': True,
        'message': 'Товар добавлен в корзину!',
        'cart_count': cart_count
    })


# Страница корзины
@app.route('/cart')
@login_required
def cart():
    db_sess = db_session.create_session()
    cart_items = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()

    # Рассчитываем итоговую стоимость
    total = 0
    for item in cart_items:
        total += item.product.retail_price_with_vat * item.quantity

    return render_template(
        'cart.html',
        title='Корзина',
        cart_items=cart_items,
        total=total
    )


# Обновление количества товара в корзине
@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    db_sess = db_session.create_session()
    cart_item = db_sess.query(CartItem).get(item_id)

    if cart_item and cart_item.user_id == current_user.id:
        action = request.form.get('action')
        if action == 'increment':
            cart_item.quantity += 0.5
        elif action == 'decrement' and cart_item.quantity > 0.5:
            cart_item.quantity -= 0.5

        db_sess.commit()

    return redirect(url_for('cart'))


# Оформление заказа
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    db_sess = db_session.create_session()
    cart_items = db_sess.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()

    if not cart_items:
        flash('Корзина пуста!', 'warning')
        return redirect(url_for('cart'))

    # Создаем заказ для каждого товара
    for item in cart_items:
        product = item.product
        order = Order(
            user_id=current_user.id,
            product_id=product.id,
            unit=product.unit,
            price_per_unit=product.retail_price_with_vat,
            quantity=item.quantity,
            total_price=product.retail_price_with_vat * item.quantity,
            discount=0.0,  # Можно добавить расчет скидки
            discounted_price=product.retail_price_with_vat * item.quantity,
            tax=0.0,  # Можно добавить расчет налога
            order_number=f"ORD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}",
            status='новый'  # Статус заказа
        )
        db_sess.add(order)
        db_sess.delete(item)

    db_sess.commit()
    flash('Заказ оформлен! Статус: новый', 'success')
    return redirect(url_for('user_orders'))


# Главная функция запуска приложения
if __name__ == '__main__':
    # Инициализация базы данных с PostgreSQL
    db_session.global_init(app.config['SQLALCHEMY_DATABASE_URI'])

    # # Создаем сессию для работы с БД
    # db_sess = db_session.create_session()
    #
    # # Импортируем необходимые модели
    # from data.loyalty import LoyaltyLevel
    # from data.customers import Customer
    #
    # # Проверяем и создаем начальные данные, если их нет
    # # Создаем уровни лояльности, если их нет
    # if not db_sess.query(LoyaltyLevel).first():
    #     levels = [
    #         LoyaltyLevel(id=0, level_name="Базовый", discount=0.0, min_purchases=0, min_total=0),
    #         LoyaltyLevel(id=1, level_name="Серебряный", discount=5.0, min_purchases=10, min_total=5000),
    #         LoyaltyLevel(id=2, level_name="Золотой", discount=10.0, min_purchases=30, min_total=15000),
    #         LoyaltyLevel(id=3, level_name="Администратор", discount=0.0, min_purchases=0, min_total=0)
    #     ]
    #     db_sess.add_all(levels)
    #     db_sess.commit()
    #
    # # Создаем администратора, если его нет
    # if not db_sess.query(Customer).filter(Customer.email == 'admin@example.com').first():
    #     admin = Customer(
    #         name="Prime",
    #         email="ganef85@mail.ru",
    #         phone="+7(950)012-40-11",
    #         street="-",
    #         building="-",
    #         status=5,  # Статус администратора
    #         loyalty_level=5  # Уровень лояльности "Prime"
    #     )
    #     admin.set_password("Tdutif_85")
    #     db_sess.add(admin)
    #     db_sess.commit()

    # Запуск приложения
    # app.run(host='localhost', port=5000, debug=debug)  #

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
