/**
 * Глобальная функция для обработки отправки контактной формы
 * @param {Event} event - Событие отправки формы
 */
document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // Обработка формы
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }

    // Инициализация карты
    if (typeof initMap === 'function' && document.getElementById('map')) {
        const mapElement = document.getElementById('map');
        const center = JSON.parse(mapElement.dataset.center);
        const logoPath = mapElement.dataset.logo;
        initMap(center, 16, 'map', logoPath);
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

    // Обработчик для кнопок "В корзину" на странице товаров
    function setupAddToCartButtons() {
        const cartForms = document.querySelectorAll('form[action*="/add_to_cart"]');
        cartForms.forEach(form => {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                try {
                    const formData = new FormData(this);
                    const response = await fetch(this.action, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': '{{ csrf_token() }}' // CSRF-токен для защиты
                        },
                        body: JSON.stringify(Object.fromEntries(formData))
                    });

                    if (!response.ok) throw new Error('Network response was not ok');

                    const result = await response.json();
                    if (result.success) {
                        // Обновляем счетчик
                        updateCartCounter(result.cart_count);

                        // Показываем уведомление
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

    // Обработчик для изменения количества товара в корзине (плюс/минус)
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

                    // Перезагружаем страницу корзины для обновления данных
                    window.location.reload();
                } catch (error) {
                    console.error('Error updating cart:', error);
                    showNotification('Ошибка при обновлении корзины', 'error');
                }
            });
        });
    }

    // Обработчик для оформления заказа
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
                        // Перенаправляем на страницу заказов через 2 секунды
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
        // Получаем количество товаров в корзине при загрузке
        fetchCartCount();

        // Настраиваем кнопки добавления в корзину
        if (document.querySelector('form[action*="/add_to_cart"]')) {
            setupAddToCartButtons();
        }

        // Настраиваем элементы управления количеством в корзине
        if (document.querySelector('.quantity-control form')) {
            setupQuantityControls();
        }

        // Настраиваем кнопку оформления заказа
        if (document.getElementById('checkout-form')) {
            setupCheckoutButton();
        }
    }

    // Запускаем инициализацию корзины
    initCartFunctionality();
});

async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;

    try {
        // Собираем данные формы
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        console.log('Отправляемые данные:', data);

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

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Создаем иконку в зависимости от типа уведомления
    const icon = document.createElement('i');
    icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';

    // Создаем текстовый элемент
    const text = document.createElement('span');
    text.textContent = message;

    // Собираем уведомление
    notification.appendChild(icon);
    notification.appendChild(text);

    // Стилизация уведомления
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

    // Добавляем анимацию исчезновения
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Код, выполняемый после полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM полностью загружен");

    // ======================
    // Мобильное меню
    // ======================
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    if (menuToggle && navMenu) {
        // Переключение видимости мобильного меню
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            console.log("Мобильное меню переключено");
        });

        // Закрытие меню при клике на пункт
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    console.log("Мобильное меню закрыто");
                }
            });
        });
    }

    // ======================
    // Обработка кнопки входа
    // ======================
    const registerBtn = document.querySelector('.btn-primary');
    if (registerBtn && registerBtn.textContent.includes('Войти')) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Перенаправление на страницу входа");
            window.location.href = "/login";
        });
    }

    // ======================
    // Инициализация карты
    // ======================
    if (typeof initMap === 'function' && document.getElementById('map')) {
        console.log("Инициализация карты");
        const mapElement = document.getElementById('map');
        const center = JSON.parse(mapElement.dataset.center);
        const logoPath = mapElement.dataset.logo;

        initMap(center, 16, 'map', logoPath);
    }

    // ======================
    // Дополнительная отладка
    // ======================
    // Проверяем, что форма существует и обработчик назначен
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        console.log("Контактная форма найдена");
        // Дублируем обработчик для отладки
        contactForm.addEventListener('submit', handleFormSubmit);
    } else {
        console.warn("Контактная форма не найдена");
    }

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