# Цифровой профиль

Одностраничный статический сайт: диджитал-витрина, хаб ссылок и один проект. RU + EN.

## Локальная разработка

```bash
pip install -r requirements.txt
python build.py
python -m http.server --directory dist
```

- RU: http://localhost:8000/
- EN: http://localhost:8000/en/

Контент и URL — плейсхолдеры в `templates/index.ru.html` и `templates/index.en.html`. PNG — в `assets/images/` (сжатие Pillow при сборке).

## Публикация на GitHub Pages

Сайт собирается в CI и выкладывается из `dist/` (папка в `.gitignore`, в репозиторий не коммитится).

### Один раз

1. Создайте репозиторий на GitHub и привяжите remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin master
   ```
2. **Settings → Pages → Build and deployment → Source:** `GitHub Actions`.
3. Дождитесь зелёного workflow **Deploy to GitHub Pages** во вкладке Actions.

### URL сайта

| Тип репозитория | Адрес |
|-----------------|--------|
| `username.github.io` | `https://username.github.io/` |
| любой другой | `https://username.github.io/имя-репозитория/` |

`SITE_BASE_URL` для Open Graph подставляется автоматически в CI. Локально можно задать вручную:

```bash
# Windows PowerShell
$env:SITE_BASE_URL="https://username.github.io/repo-name"; python build.py
```

### Обновления

Правки в шаблонах → `git push` → Actions пересоберёт и задеплоит сайт.

## Документация

- [план-цифровой-профиль.md](план-цифровой-профиль.md) — этапы и решения
- [wireframe.md](wireframe.md) — структура страницы
- [контент-чеклист.md](контент-чеклист.md) — что подготовить для контента

## Ссылки (замените на свои)

- Сайт: `https://github.com/your_username` → после деплоя укажите URL Pages в био соцсетей
- Репозиторий: `https://github.com/your_username/your-repo`
