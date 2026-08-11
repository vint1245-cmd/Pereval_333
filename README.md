**Pereval FSTR API**

Короткая документация и примеры для проекта "Pereval" — FastAPI-реализация API приёмки данных о горных перевалах для итоговой аттестации SkillFactory.

**Содержание**
- **Описание:** кратко о назначении API.
- **Требования:** зависимости и совместимость.
- **Установка:** шаги для разворачивания локально.
- **Переменные окружения:** список важных переменных.
- **Запуск:** команды для разработки и продакшна.
- **API:** подробное описание эндпоинтов и примеры запросов/ответов.
- **Валидация:** правила для полей (изображения, телефон и т.д.).
- **Тестирование:** как запускать тесты.
- **Отладка:** типичные проблемы и решения.

**Описание**

API принимает данные от мобильного приложения: информацию о перевале, контактные данные пользователя и фотографии. Администраторы модерации изменяют поле `status` у объекта (new → pending → accepted/rejected).

Проектная структура: смотрите папку [pereval_fastapi](pereval_fastapi).

**Требования**
- **Python:** 3.10+ (проект тестирован в venv, см. `pereval_fastapi/.venv`).
- **Зависимости:** перечислены в `pereval_fastapi/requirements.txt`.

Установить зависимости:

```
python -m pip install -r pereval_fastapi/requirements.txt
```

**Переменные окружения**
- **`DATABASE_URL`** — полный URL для async SQLAlchemy (рекомендуется `postgresql+asyncpg://...`).
- или альтернативы: `FSTR_DB_LOGIN`, `FSTR_DB_PASS`, `FSTR_DB_HOST`, `FSTR_DB_PORT`, `FSTR_DB_NAME` — если `DATABASE_URL` не задан, приложение попытается собрать URL по частям.
- **`TEST_DATABASE_URL`** — используется в тестах (по умолчанию `sqlite+aiosqlite:///:memory:`).

Если переменные не заданы, по умолчанию используется SQLite файл `pereval.db` внутри `pereval_fastapi`.

**Запуск приложения (локально)**

Для разработки:

```
cd pereval_fastapi
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Если используете виртуальное окружение на Windows:

```
.
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

**API Эндпоинты** (префикс `/api/v1`)

**1) Создать запись**
- Метод: `POST`
- Путь: `/api/v1/submitData`
- Описание: создаёт новую запись перевала. Если пользователь с таким `email` уже есть — он переиспользуется.
- Тело запроса: JSON (пример ниже).
- Успешный ответ: `200` и тело `{ "status": 200, "message": null, "id": <int> }`.

Пример запроса (JSON):

```json
{
  "beauty_title": "пер. Тестовый",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "г. A - г. B",
  "add_time": "2024-01-01 12:00:00",
  "user": { "email": "q@q.q", "fam": "Иванов", "name": "Иван", "otc": "Ив", "phone": "+79991234567" },
  "coords": { "latitude": 45.3842, "longitude": 7.1525, "height": 1200 },
  "level": { "winter": "", "summer": "1А", "autumn": "1А", "spring": "" },
  "images": [ { "data": "<base64>", "title": "Седловина" } ]
}
```

Ошибки: `400` для неверного/неполного запроса, `500` при ошибках сервера.

**2) Получить запись по ID**
- Метод: `GET`
- Путь: `/api/v1/submitData/{id}`
- Описание: возвращает детальную информацию о перевале, включая `user`, `coords`, `level`, `images` и `status`.

Успешный ответ: `200` и JSON со структурой перевала.

**3) Список по email**
- Метод: `GET`
- Путь: `/api/v1/submitData?user__email={email}`
- Описание: возвращает список записей, отправленных пользователем с указанным email.

**4) Редактирование записи**
- Метод: `PATCH`
- Путь: `/api/v1/submitData/{id}`
- Описание: выполняет замену полей записи, если она в статусе `new`.
- Ограничения: нельзя менять поля `user.email`, `user.fam`, `user.name`, `user.otc`, `user.phone`.
- Поддерживает удаление изображений через поле `images_to_delete` — массив id изображений.
- Успешный ответ: `200` и тело `{ "state": 1, "message": "Запись успешно отредактирована" }`.

Если статус записи !== `new`, возвращается `409` (или `400`) с описанием.

**Валидация полей**
- **Изображения:** поле `data` должно содержать корректную Base64-строку; допускается префикс `data:...;base64,` — приложение удалит префикс и проверит содержимое.
- **Телефон:** нормализуется и проверяется по шаблону `+79991234567` (7–15 цифр), при некорректном формате возвращается ошибка валидации.

**Структуры Pydantic / Модели**
- Основные схемы находятся в [pereval_fastapi/app/schemas](pereval_fastapi/app/schemas).
- Основные модели SQLAlchemy — в [pereval_fastapi/app/models](pereval_fastapi/app/models).

**Тестирование**

Запуск тестов:

```
cd pereval_fastapi
python -m pytest -q
```

Фикстуры используют in-memory SQLite по умолчанию (`TEST_DATABASE_URL`), поэтому внешняя БД не требуется для тестов.

**Отладка и типичные проблемы**
- Если `uvicorn` не запускается: проверьте правильность `PYTHONPATH` и текущее рабочее дерево — запускайте из `pereval_fastapi` или передавайте `--app-dir`.
- Порт занят: укажите другой порт с помощью `--port`.
- Ошибки миграций/моделей: убедитесь, что все модели импортируются в `pereval_fastapi/app/db.py`.

**Полезные файлы**
- Основной FastAPI-приложение: [pereval_fastapi/app/main.py](pereval_fastapi/app/main.py)
- Роутер submitData: [pereval_fastapi/app/routers/submitdata.py](pereval_fastapi/app/routers/submitdata.py)
- Сервисная логика: [pereval_fastapi/app/services/submit_service.py](pereval_fastapi/app/services/submit_service.py)
- Тесты: [pereval_fastapi/tests/test_submitdata.py](pereval_fastapi/tests/test_submitdata.py)

**Лицензия**
- Код проекта находится под свободной лицензией (уточните в репозитории при необходимости).
