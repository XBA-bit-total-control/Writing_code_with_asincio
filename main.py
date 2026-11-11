from sqlalchemy.exc import ProgrammingError, IntegrityError
from aiohttp.client_exceptions import ContentTypeError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func
from db import Characters, Session
from itertools import batched
from datetime import datetime

import asyncio
import aiohttp


async def get_person(id, client):
    """
    Асинхронная функция для получения персонажа
    """
    response = await client.get(f"https://www.swapi.tech/api/people/{id}")
    data = await response.json()
    if data["message"] == "ok":
        return data["result"]["properties"]
    else:
        return None


async def get_planet(path, client):
    """
    Асинхронная функция для получения планеты
    """
    response = await client.get(path)
    data = await response.json()
    return data["result"]["properties"]["name"]


async def main():
    try:
        client = aiohttp.ClientSession()
        async with Session() as session:
            for set_id in batched(range(1, 84), 5):
                coros_pers = [get_person(id, client) for id in set_id]

                person = await asyncio.gather(*coros_pers)

                # Такая тяжелая логика была сделана из-за того, что персонажа с id 17 нет в API
                # Так как сам API не изменяется можно было бы просто запрос для него не отсылать
                # Но я решил оставить так - кода стало немного меньше, но логика такая же громоздкая

                person = {ind: data for ind, data in enumerate(person) if data is not None}
                set_id = [id for ind, id in enumerate(set_id) if ind in person.keys()]

                planet_url = [data["homeworld"] for data in person.values()]
                coros_plans = [get_planet(path, client) for path in planet_url]

                planet = await asyncio.gather(*coros_plans)

                for per, pl, id in zip(person.values(), planet, set_id):
                    stmt = insert(Characters).values(
                        id=id,
                        birth_year=per["birth_year"],
                        eye_color=per["eye_color"],
                        gender=per["gender"],
                        hair_color=per["hair_color"],
                        homeworld=pl,
                        mass=per["mass"],
                        name=per["name"],
                        skin_color=per["skin_color"]
                    )
                    stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
                    await session.execute(stmt)
                    print(f"Получен {per["name"]}", f"{(35 - len(per["name"])) * " "} - номер {id}")
                await session.commit()

        # Проверка на получение всех персонажей
        async with Session() as session:
            all_entries = await session.execute(select(func.count()).select_from(Characters))
            all_entries = all_entries.scalar()
            if all_entries == 82:
                print("Все 82 персонажа успешно получены и записаны в базу")
            else:
                print(f"Не все персонажи были получены - недостаёт {82 - all_entries}")

    except IntegrityError:
        raise AssertionError("В базе данных уже есть такая запись")
    except ProgrammingError:
        raise AssertionError("Таблица для записи не была создана в БД")
    except ContentTypeError:
        raise AssertionError("Отправлено слишком большое количество запросов")
    except Exception as err:
        raise AssertionError(f"Произошла ошибка {err.__class__.__name__}")
    finally:
        await client.close()


start = datetime.now()
asyncio.run(main())
print("Данные получены за:", datetime.now() - start)
