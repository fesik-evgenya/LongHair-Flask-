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
    notification.textContent = message;

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
        animation: 'slideIn 0.3s ease-out'
    });

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
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
        contactForm.addEventListener('submit', sendContactForm);
    } else {
        console.warn("Контактная форма не найдена");
    }
});