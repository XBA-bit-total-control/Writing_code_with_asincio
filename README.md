### Программа написана с асинхронным подходом и использованием библиотек asyncio и aiohttp

Для запуска требуется:

1. Создать и заполнить .env-файл
2. Создать и активировать виртуальное окружение
```bash
python3 -m venv .venv && source .venv/bin/activate
```
3. Установить библиотеки из requirements.txt
```bash
pip install -r requirements.txt
```
4. Запустить контейнер postgres при необходимости
```bash
docker-compose up
```
5. Произвести миграции
```bash
./migrate.py
```
6. Запустить программу
```bash
./main.py
```

Примечание: В .env-example в качестве значения для POSTGRES_DRIVER уже указаны рекомендуемые значения 