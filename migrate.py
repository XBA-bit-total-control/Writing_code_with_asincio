from db import open_orm, close_orm
import asyncio


async def main():
    await open_orm()
    await close_orm()


try:
    asyncio.run(main())
    print("Таблица 'characters' успешно создана")
except Exception as err:
    print(f"Создание таблицы завершилось неудачей из-за ошибки {err.__class__.__name__}")
