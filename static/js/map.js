/**
 * Инициализация Яндекс.Карты с логотипом компании в качестве метки
 * @param {Array} center - Координаты центра [широта, долгота]
 * @param {number} zoom - Уровень масштабирования
 * @param {string} elementId - ID контейнера для карты
 * @param {string} logoPath - Путь к логотипу компании
 */
function initMap(center = [59.824518, 30.337296], zoom = 16, elementId = 'map', logoPath) {
    // Проверяем загрузку API Яндекс.Карт
    if (typeof ymaps === 'undefined') {
        console.error('Yandex Maps API not loaded');
        return;
    }

    ymaps.ready(() => {
        // Создаем карту в указанном контейнере
        const myMap = new ymaps.Map(elementId, {
            center: center,
            zoom: zoom,
            controls: ['zoomControl']
        });

        // Размеры метки (уменьшены в 2 раза)
        const iconSize = [30, 30];
        const iconOffset = [-15, -15];
        const shadowSize = [35, 35];

        // Создание кастомной метки с логотипом компании
        const myPlacemark = new ymaps.Placemark(
            center,
            {
                balloonContent: '<strong>Фруктовый Район</strong><br>Свежие фрукты и овощи',
                hintContent: 'Наш магазин'
            },
            {
                // Используем логотип компании как иконку
                iconLayout: 'default#image',
                iconImageHref: logoPath,
                iconImageSize: iconSize,
                iconImageOffset: iconOffset,

                // Область клика
                iconShape: {
                    type: 'Circle',
                    coordinates: [0, 0],
                    radius: 15
                },

                // Тень
                iconShadow: true,
                shadowImageHref: logoPath,
                shadowImageSize: shadowSize,
                shadowOffset: [3, 8],
                shadowOpacity: 0.2
            }
        );

        // Добавляем метку на карту
        myMap.geoObjects.add(myPlacemark);

        // Открываем балун при клике на метку
        myPlacemark.events.add('click', function() {
            myPlacemark.balloon.open();
        });

        // Анимация пульсации (меняем размер каждые 1.5 секунды)
        setInterval(() => {
            const icon = myPlacemark.options.get('iconImageSize');
            const newSize = icon[0] === 30 ? [32, 32] : [30, 30];
            myPlacemark.options.set('iconImageSize', newSize);
        }, 1500);
    });
}