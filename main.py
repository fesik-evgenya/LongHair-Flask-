from flask import Flask, url_for, request, render_template, redirect
from flask_login import LoginManager, current_user
from werkzeug.utils import secure_filename
import os.path
import sqlite3
from forms.loginform import LoginForm
from data import db_session
from sqlite3 import Error
from data.users import User
from data.news import News
from forms.user import Register

# регистрируем приложение
app = Flask(__name__)

app.secret_key = 'Tdutif_85'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'zip', 'jpg', 'png']
debug = False

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Заглушка для user_loader
@login_manager.user_loader
def load_user(user_id):
    return None

# обработка 404
@app.errorhandler(404)
def not_found(y):
    return render_template('404.html', title="Не найдено")

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template('index.html', title="Район {Фруктовый}")

# Добавленные маршруты
@app.route('/about')
def about():
    return render_template('about.html', title="Район {Фруктовый} | О нас")

@app.route('/goods')
def goods():
    return render_template('goods.html', title="Район {Фруктовый} | Товары")

@app.route('/contacts')
def contacts():
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

if __name__ == '__main__':
    # db_session.global_init('../shop_Fruit-District/db/news.sqlite')
    app.run(host='localhost', port=5000, debug=debug)