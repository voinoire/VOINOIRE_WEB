# Цифровой профиль

Статический сайт-визитка на **HTML + Python (Jinja2)**.

## Структура

```
├── templates/          # шаблоны — правите тексты здесь
│   ├── base.html       # стили, header, footer
│   ├── index.ru.html   # русская версия
│   └── index.en.html   # английская версия
├── assets/             # картинки, PDF резюме
├── build.py            # сборка в dist/
└── dist/               # готовый сайт для публикации
```

## Быстрый старт

```bash
pip install -r requirements.txt
python build.py
python -m http.server --directory dist
```

- RU: http://localhost:8000/
- EN: http://localhost:8000/en/

## Что делать дальше

1. Заменить placeholder-тексты в `templates/index.ru.html` и `templates/index.en.html`
2. Настроить стили в `templates/base.html` (блок `:root`)
3. Добавить фото в `assets/images/`
4. Указать ссылку на GitHub в блоке контактов
5. Опубликовать папку `dist/` на GitHub Pages

## GitHub

Ссылка на профиль: _добавить позже_
