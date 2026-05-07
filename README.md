# FreelanceDesk

Веб-застосунок-візитка для ФОП у сфері веб-розробки. Поєднує маркетинговий сайт, інтерактивний калькулятор вартості та адмін-панель для обробки заявок.

---

## Можливості

- **Калькулятор вартості** — миттєво рахує ціну за формулою з урахуванням послуги, технологічного стеку, терміну та обсягу
- **Форма заявки** — гість надсилає запит без реєстрації; контакт у довільному форматі (телефон / Telegram / email)
- **Адмін-панель** — повний CRUD послуг та технологій, перегляд і обробка заявок, редагування налаштувань сайту
- **API** — JSON-ендпоінти для калькулятора та адміністрування
- **Без збірки фронтенду** — Vue 3 через CDN, жодного npm / webpack

---

## Стек

| Шар | Технологія |
|---|---|
| Backend | Python 3.11+, Flask 3.0+ |
| ORM | SQLAlchemy 2.0+, SQLite |
| Авторизація | Flask-Login 0.6+ (сесії) |
| CSRF | Flask-WTF 1.2+ |
| Frontend | Vue 3.4 (CDN global build) |
| Стилі | Власний CSS (темна тема, анімації, паралакс) |

---

## Дизайн

Темна тема у природній кольоровій палітрі:

| Назва | HEX | Де використовується |
|---|---|---|
| Prussian Blue | `#103A57` | Фон поверхонь |
| Teal Blue | `#307B8E` | Акцент, кнопки, посилання |
| Pastel Blue | `#A9D3C5` | Приглушений текст |
| Light Silver | `#CEE5D6` | Основний текст |
| Mughal Green | `#366B2B` | Успішні стани |

Hero-секція: фото фону (Unsplash) + паралакс + SVG-сітка + плаваючі code-фрагменти. Карусель послуг із авто-прокруткою та glassmorphism-карткою. Scroll-reveal анімації через IntersectionObserver.

---

## Швидкий старт (Windows)

```
Двічі клацнути start.bat
```

Батник автоматично:
1. Перевіряє наявність Python
2. Створює virtualenv
3. Встановлює залежності
4. Ініціалізує та заповнює БД
5. Відкриває браузер на `http://127.0.0.1:5001/`

---

## Ручний запуск

```bash
cd freelancedesk

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

# Ініціалізація БД (першого разу)
flask --app run.py db-init
flask --app run.py seed

# Сервер розробки
flask --app run.py run --port 5001
```

Сайт: `http://127.0.0.1:5001/`

> **Windows:** порт 5000 заблокований Hyper-V — використовується 5001.

---

## Адмін-панель

| Параметр | Значення |
|---|---|
| URL | `http://127.0.0.1:5001/admin/login` |
| Логін | `admin` |
| Пароль | `admin123` |

Змінити пароль: `Налаштування` → поле пароля (або через змінну середовища `ADMIN_INITIAL_PASSWORD` до першого `seed`).

### Розділи адмін-панелі

- **Дашборд** — лічильники нових заявок, останні 5 заявок
- **Заявки** — перегляд, фільтрація за статусом, зміна статусу, видалення
- **Послуги** — CRUD, прив'язка технологій, деактивація / видалення
- **Технології** — CRUD, множник ціни
- **Налаштування** — назва сайту, слоган, адреса, короткий опис

---

## Формула розрахунку ціни

```
P = B × V × M_tech × K(D)

K(D) = 1 + α × e^(−β × (D − 1))
```

| Змінна | Опис | За замовч. |
|---|---|---|
| B | Базова ціна послуги (₴/од.) | залежить від послуги |
| V | Обсяг (кількість сторінок / модулів) | ≥ 1 |
| M_tech | Множник технології | 0.90 – 1.50 |
| D | Термін виконання (днів) | ≥ 1 |
| α | Амплітуда надбавки за терміновість | 1.5 |
| β | Швидкість загасання | 0.10 |

**Приклади K(D):**

| Термін | Коефіцієнт |
|---|---|
| 1 день | 2.50× |
| 7 днів | ~1.82× |
| 14 днів | ~1.41× |
| 30 днів | ~1.08× |
| 60 днів | ~1.00× |

Формула реалізована **двічі** — у Python (`app/calculator.py`) та JavaScript (`static/js/calculator.js`) — і дає ідентичний результат. Серверна є авторитетною: при подачі заявки ціна перераховується на сервері незалежно від клієнтського значення.

---

## API

### Публічні (без авторизації)

| Метод | URL | Опис |
|---|---|---|
| GET | `/api/services` | Список активних послуг із технологіями |
| GET | `/api/technologies` | Список активних технологій |
| POST | `/api/calculate` | Серверний розрахунок ціни |
| POST | `/api/requests` | Подача заявки гостем |

#### POST /api/calculate

```json
// Запит
{ "service_id": 1, "technology_id": 6, "deadline_days": 3, "volume": 1 }

// Відповідь
{
  "final_price": 8355.36,
  "breakdown": {
    "base_price": 2500.0,
    "volume": 1,
    "subtotal_after_volume": 2500.0,
    "tech_multiplier": 1.5,
    "subtotal_after_tech": 3750.0,
    "urgency_coefficient": 2.2281,
    "deadline_days": 3,
    "final_price": 8355.36
  }
}
```

#### POST /api/requests

```json
// Запит
{
  "client_name": "Іван Петренко",
  "client_contact": "@ivan_tg",
  "service_id": 1,
  "technology_id": 2,
  "deadline_days": 14,
  "volume": 3,
  "comment": "Лендинг для кав'ярні"
}

// Відповідь 201
{ "success": true, "request_id": 42, "calculated_price": 8145.0 }
```

### Адмін (потребує авторизації)

| Метод | URL | Опис |
|---|---|---|
| GET | `/api/admin/requests` | Список заявок |
| PATCH | `/api/admin/requests/<id>/status` | Зміна статусу |

```json
// PATCH /api/admin/requests/42/status
{ "status": "in_progress" }
// Допустимі статуси: new, in_progress, done, rejected
```

---

## Структура проєкту

```
freelancedesk/
├── app/
│   ├── __init__.py          # Фабрика create_app()
│   ├── extensions.py        # db, login_manager, csrf
│   ├── models.py            # User, Service, Technology, ClientRequest, SiteSetting
│   ├── calculator.py        # Формула розрахунку ціни
│   ├── forms_validators.py  # Серверна валідація
│   ├── auth.py              # Login / Logout + rate limit
│   ├── routes_public.py     # /, /services, /about, /contact
│   ├── routes_admin.py      # /admin/* (CRUD)
│   ├── routes_api.py        # /api/* (JSON)
│   ├── seed.py              # CLI: flask seed, flask db-init
│   ├── templates/
│   │   ├── base.html
│   │   ├── admin/
│   │   └── public/
│   │       ├── index.html   # Hero + карусель послуг (Vue 3)
│   │       ├── services.html # Список послуг + калькулятор (Vue 3)
│   │       ├── about.html
│   │       └── contact.html
│   └── static/
│       ├── css/main.css
│       ├── js/
│       │   ├── calculator.js
│       │   ├── admin.js
│       │   └── public.js
│       └── img/favicon.svg
├── instance/
│   └── app.db               # SQLite (створюється автоматично)
├── config.py
├── run.py
├── requirements.txt
├── start.bat                # Запуск одним кліком (Windows)
└── README.md
```

---

## Конфігурація

Файл `config.py` або змінні середовища (`.env`):

| Змінна | За замовч. | Опис |
|---|---|---|
| `SECRET_KEY` | *(небезпечне)* | Ключ підпису сесій. **Обов'язково змінити в продакшні** |
| `ADMIN_INITIAL_PASSWORD` | `admin123` | Пароль адміна при першому `seed` |
| `URGENCY_ALPHA` | `1.5` | Амплітуда коефіцієнта терміновості |
| `URGENCY_BETA` | `0.10` | Швидкість загасання |

Приклад `.env`:
```
SECRET_KEY=ваш-дуже-довгий-рандомний-рядок
ADMIN_INITIAL_PASSWORD=SuperSecret123!
URGENCY_ALPHA=1.5
URGENCY_BETA=0.10
```

---

## Валідація

| Поле | Правило |
|---|---|
| `client_name` | 2–128 символів |
| `client_contact` | 5–255 символів (телефон / Telegram / email) |
| `deadline_days` | Ціле, 1–365 |
| `volume` | Ціле, 1–1000 |
| `comment` | ≤ 4000 символів |
| `base_price` | > 0 |
| `multiplier` | > 0 |

Брутфорс-захист входу в адмінку: 5 спроб за 15 хвилин з однієї IP-адреси.

---

## Розгортання (продакшн)

### Linux + gunicorn + nginx

```bash
pip install gunicorn
gunicorn -w 2 -b 127.0.0.1:8000 "app:create_app()"
```

nginx (`/etc/nginx/sites-available/freelancedesk`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/freelancedesk/app/static/;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Windows + waitress

```bash
pip install waitress
waitress-serve --port=8000 --call "app:create_app"
```

### Бекап БД

```bash
# Cron: щодня о 3:00
0 3 * * * cp /path/to/instance/app.db /backups/app-$(date +\%Y\%m\%d).db
```

---

## Команди розробки

```bash
# Ініціалізація БД (без seed-даних)
flask --app run.py db-init

# Заповнення тестовими даними
flask --app run.py seed

# Запуск у режимі debug
FLASK_DEBUG=1 flask --app run.py run --port 5001

# Перегляд маршрутів
flask --app run.py routes
```

---

## Початкові дані (seed)

### Послуги

| Назва | Базова ціна |
|---|---|
| Лендинг (одна сторінка) | 2 500 ₴ |
| Корпоративний сайт | 1 800 ₴/стор. |
| Інтернет-магазин | 3 500 ₴/модуль |
| Веб-застосунок | 4 500 ₴/модуль |
| Telegram-бот | 2 000 ₴/модуль |
| API-інтеграція | 1 200 ₴/ендпоінт |
| Технічна підтримка | 600 ₴/год. |

### Технології

| Назва | Множник |
|---|---|
| Django + SQLite | 0.90 |
| Flask + Vue | 1.00 |
| Laravel + Vue | 1.10 |
| React + Node.js | 1.20 |
| Spring Boot | 1.30 |
| Blazor Server (.NET) | 1.50 |

Усі технології прив'язані до всіх послуг за замовчуванням. Зв'язки можна змінити через адмін-панель.
