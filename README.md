<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=250&section=header&text=Все%20по%20полочкам&fontSize=60&fontAlignY=38&desc=Magda%20AI%20Agent&descAlignY=55&descAlign=62" alt="Все по полочкам Header"/>

  <p align="center">
    <i>Автономный когнитивный агент с системой самосовершенствования</i>
  </p>

  <p align="center">
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"></a>
    <a href="https://core.telegram.org/"><img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"></a>
    <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
    <a href="https://docs.pytest.org/"><img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest"></a>
  </p>
</div>

---

## 🌟 О проекте

**«Все по полочкам»** — это продвинутый экспериментальный ИИ-агент (на базе архитектуры Magda Agent), спроектированный как цифровая модель сознания. Агент не просто отвечает на вопросы, он обладает памятью, эмоциями, способностью к планированию и, самое главное, механизмом **автономного самосовершенствования**.

### Ключевые возможности:
- 🧠 **Когнитивная архитектура:** Разделение на специализированные модули (таламус, гиппокамп, префронтальная кора).
- 💾 **Многоуровневая память:** Краткосрочная (Working Memory), эпизодическая (Episodic) и семантическая (Semantic).
- 🎭 **Эмоциональный движок:** Модель PAD (Удовольствие, Возбуждение, Доминирование), влияющая на стиль общения.
- 🎯 **Планирование:** Разрезание сложных задач на последовательные шаги и использование внешних навыков (Skills).
- 🤖 **Self-Improvement:** Встроенный цикл Jules, который автономно правит код, добавляет тесты и внедряет новые функции.
- 🔌 **Протоколы будущего:** Поддержка MCP (Model Context Protocol) и A2A (Agent-to-Agent).

---

## 🧠 Когнитивная Архитектура

Агент построен по модульному принципу, имитирующему работу биологического мозга:

1.  **Thalamus (Таламус):** Входной шлюз. Фильтрует шум, нормализует ввод и определяет приоритетность.
2.  **Salience Network:** Определяет, что заслуживает внимания прямо сейчас (важность, риск, новизна).
3.  **Global Workspace:** «Сцена» сознания, где конкурирующие идеи и события объединяются в единый контекст.
4.  **Prefrontal Cortex (Планировщик):** Превращает намерения в пошаговые планы действий.
5.  **Emotional Engine:** Управляет «настроением» агента, которое меняется в зависимости от контекста и истории общения.
6.  **Basal Ganglia:** Отвечает за окончательный выбор действия из нескольких альтернатив.

---

## 🚀 Инструкция по использованию

### 1. Подготовка окружения

Убедитесь, что у вас установлен Python 3.12+.

```bash
# Клонируйте репозиторий
git clone https://github.com/your-repo/magda-agent.git
cd magda-agent

# Создайте и активируйте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
# или
venv\Scripts\activate     # Для Windows

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Отредактируйте `.env`, добавив ваши ключи:
- `TELEGRAM_BOT_TOKEN`: Токен вашего бота от @BotFather.
- `OPENAI_API_KEY`: Ваш ключ OpenAI (или другого провайдера LLM).

### 3. Запуск агента

Проект состоит из нескольких сервисов. Вы можете запустить их по отдельности или через Docker.

**Через Docker Compose (рекомендуется):**
```bash
docker-compose up -d
```

**Вручную:**
```bash
# Запуск API сознания (FastAPI)
python -m magda_agent.api

# Запуск Telegram-бота (в другом терминале)
python -m magda_agent.main
```

---

## 🤖 Автономный цикл (Jules)

Агент способен развивать сам себя через систему **Jules**.

- **Манифест задач:** Все задачи хранятся в [agent_tasks.json](agent_tasks.json).
- **Приоритет:** Jules берет первую задачу со статусом `todo` и реализует её.
- **Безопасность:** Каждое изменение проходит через систему рисков (Amygdala/RiskSystem) и тесты.

**Команды для работы с задачами:**
```bash
# Проверить статус очереди задач
python -m magda_agent.codex_bridge status

# Валидация манифеста
python scripts/validate_agent_tasks.py agent_tasks.json

# Получить следующую задачу для реализации
python -m magda_agent.codex_bridge next-task
```

---

## 🧪 Разработка и тестирование

Мы придерживаемся строгих стандартов качества:
- Обязательная типизация (Type Hints).
- Наличие docstring у каждой функции.
- Покрытие тестами (pytest) с моками для всех внешних API.

**Запуск тестов:**
```bash
pytest tests/
```

---

## 📈 Тренды и будущее

Мы следим за развитием ИИ-агентов. Наши ориентиры на июнь 2026 года описаны в [docs/trends.md](docs/trends.md). Мы внедряем поддержку:
- **MCP:** Экспорт навыков как инструментов для других агентов.
- **Multi-Agent Teams:** Работа в команде с изоляцией через Git Worktrees.
- **Online Learning:** Обучение на основе обратной связи пользователя в реальном времени.

<br>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=100&section=footer" alt="Footer"/>
</div>
