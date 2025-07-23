/**
 * Основной скрипт приложения - обработчики событий и инициализация компонентов
 * @file app.js
 * @description Главный JavaScript файл, содержащий всю клиентскую логику приложения
 */

document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // МОБИЛЬНОЕ МЕНЮ
    // ======================
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    if (menuToggle && navMenu) {
        // Переключение видимости мобильного меню
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });

        // Закрытие меню при клике на пункт навигации
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                }
            });
        });
    }

    // ======================
    // ФОРМА ПОИСКА
    // ======================
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const params = new URLSearchParams(formData).toString();
            window.location.href = `{{ url_for('goods') }}?${params}`;
        });
    }

    // ======================
    // КОНТАКТНАЯ ФОРМА
    // ======================
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }

    // ======================
    // ИНИЦИАЛИЗАЦИЯ КАРТЫ
    // ======================
    if (typeof initMap === 'function' && document.getElementById('map')) {
        const mapElement = document.getElementById('map');
        const center = JSON.parse(mapElement.dataset.center);
        const logoPath = mapElement.dataset.logo;
        initMap(center, 16, 'map', logoPath);
    }

    // ======================
    // КНОПКА ВХОДА
    // ======================
    const registerBtn = document.querySelector('.btn-primary');
    if (registerBtn && registerBtn.textContent.includes('Войти')) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = "/login";
        });
    }

    // ======================
    // ФУНКЦИОНАЛ КОРЗИНЫ
    // ======================

    // Функция для обновления счетчика корзины в шапке
    function updateCartCounter(count) {
        const cartCounter = document.getElementById('cart-counter');
        if (cartCounter) {
            cartCounter.textContent = count;
            cartCounter.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    // Получение количества товаров в корзине
    async function fetchCartCount() {
        try {
            const response = await fetch('/api/cart_count');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            updateCartCounter(data.count);
        } catch (error) {
            console.error('Error fetching cart count:', error);
        }
    }

    // Обработчик для кнопок "В корзину"
    function setupAddToCartButtons() {
        const cartForms = document.querySelectorAll('form[action*="/add_to_cart"], .add-to-cart-form');
        cartForms.forEach(form => {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                try {
                    const formData = new FormData(this);
                    const response = await fetch(this.action, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': '{{ csrf_token() }}'
                        },
                        body: JSON.stringify(Object.fromEntries(formData))
                    });

                    if (!response.ok) throw new Error('Network response was not ok');

                    const result = await response.json();
                    if (result.success) {
                        updateCartCounter(result.cart_count);
                        showNotification(result.message, 'success');
                    } else {
                        showNotification(result.message, 'error');
                    }
                } catch (error) {
                    console.error('Error adding to cart:', error);
                    showNotification('Ошибка при добавлении в корзину', 'error');
                }
            });
        });
    }

    // Обработчик изменения количества товара
    function setupQuantityControls() {
        document.querySelectorAll('.quantity-control form').forEach(form => {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                const action = this.querySelector('button[type="submit"]:focus')?.value ||
                              this.querySelector('button[type="submit"]')?.value;

                if (!action) return;

                try {
                    const response = await fetch(this.action, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': '{{ csrf_token() }}'
                        },
                        body: JSON.stringify({ action })
                    });

                    if (!response.ok) throw new Error('Network response was not ok');
                    window.location.reload();
                } catch (error) {
                    console.error('Error updating cart:', error);
                    showNotification('Ошибка при обновлении корзины', 'error');
                }
            });
        });
    }

    // Обработчик оформления заказа
    function setupCheckoutButton() {
        const checkoutForm = document.getElementById('checkout-form');
        if (checkoutForm) {
            checkoutForm.addEventListener('submit', async function(e) {
                e.preventDefault();

                try {
                    const response = await fetch(this.action, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': '{{ csrf_token() }}'
                        }
                    });

                    if (!response.ok) throw new Error('Network response was not ok');

                    const result = await response.json();
                    if (result.success) {
                        showNotification(result.message, 'success');
                        setTimeout(() => {
                            window.location.href = '/orders';
                        }, 2000);
                    } else {
                        showNotification(result.message, 'error');
                    }
                } catch (error) {
                    console.error('Error during checkout:', error);
                    showNotification('Ошибка при оформлении заказа', 'error');
                }
            });
        }
    }

    // Инициализация функционала корзины
    function initCartFunctionality() {
        fetchCartCount();

        if (document.querySelector('form[action*="/add_to_cart"], .add-to-cart-form')) {
            setupAddToCartButtons();
        }

        if (document.querySelector('.quantity-control form')) {
            setupQuantityControls();
        }

        if (document.getElementById('checkout-form')) {
            setupCheckoutButton();
        }
    }

    // Запуск инициализации корзины
    initCartFunctionality();

    // ======================
    // МОДАЛЬНОЕ ОКНО НАЗНАЧЕНИЯ СОТРУДНИКОВ
    // ======================
    const assignModalElement = document.getElementById('assignEmployeesModal');
    const assignForm = document.getElementById('assignEmployeesForm');

    // Инициализация только если элементы существуют на странице
    if (assignModalElement && assignForm) {
        const assignModal = new bootstrap.Modal(assignModalElement);

        // Обработчики для кнопок назначения сотрудников
        document.querySelectorAll('.btn-edit-assignees').forEach(button => {
            button.addEventListener('click', function() {
                const orderId = this.getAttribute('data-order-id');
                const assemblerId = this.getAttribute('data-assembler-id');
                const courierId = this.getAttribute('data-courier-id');

                // Заполняем форму текущими значениями
                document.getElementById('orderId').value = orderId;
                document.getElementById('assemblerSelect').value = assemblerId || '';
                document.getElementById('courierSelect').value = courierId || '';

                // Показываем модальное окно
                assignModal.show();
            });
        });

        // Обработка отправки формы
        assignForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Отправка данных на сервер
            fetch("{{ url_for('update_order_assignees') }}", {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-CSRFToken': '{{ csrf_token() }}'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Закрываем модальное окно и обновляем страницу
                    assignModal.hide();
                    showNotification('Назначения успешно обновлены!', 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showNotification('Ошибка при обновлении: ' + data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Произошла ошибка при отправке данных', 'error');
            });
        });
    }

    // ======================
    // ДОПОЛНИТЕЛЬНЫЕ СТИЛИ
    // ======================
    // Добавляем CSS для анимации уведомлений
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
});

// ======================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
// ======================

/**
 * Обработчик отправки контактной формы
 * @param {Event} event - Событие отправки формы
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;

    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const response = await fetch('/send_contact_form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': data.csrf_token
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        showNotification(result.message, result.success ? 'success' : 'error');

        if (result.success) {
            form.reset();
        }
    } catch (error) {
        console.error('Ошибка при отправке формы:', error);
        showNotification('Ошибка при отправке формы', 'error');
    }
}

/**
 * Показывает уведомление
 * @param {string} message - Текст сообщения
 * @param {string} type - Тип уведомления (success/error)
 */
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';

    const text = document.createElement('span');
    text.textContent = message;

    notification.appendChild(icon);
    notification.appendChild(text);

    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 25px',
        borderRadius: '5px',
        zIndex: '1000',
        color: type === 'success' ? '#155724' : '#721c24',
        backgroundColor: type === 'success' ? '#d4edda' : '#f8d7da',
        border: `1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        animation: 'slideIn 0.3s ease-out'
    });

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}