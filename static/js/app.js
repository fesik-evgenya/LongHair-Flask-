document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    // Mobile menu toggle
    menuToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });

    // Закрытие мобильного меню при клике на пункт
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            if (navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
            }
        });
    });

    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Form validation
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;

            if (name && email && subject && message) {
                alert('Сообщение отправлено! Мы свяжемся с вами в ближайшее время.');
                contactForm.reset();
            } else {
                alert('Пожалуйста, заполните все поля формы.');
            }
        });
    }

    // Обработка кнопки регистрации
    const registerBtn = document.querySelector('.btn-primary');
    if (registerBtn && registerBtn.textContent.includes('Войти')) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Перенаправление на страницу входа
            window.location.href = "/login";
        });
    }

    // Инициализация карты (если есть контейнер)
    if (typeof initMap === 'function' && document.getElementById('map')) {
        // Получаем данные из data-атрибутов
        const mapElement = document.getElementById('map');
        const center = JSON.parse(mapElement.dataset.center);
        const logoPath = mapElement.dataset.logo;

        initMap(center, 16, 'map', logoPath);
    }
});