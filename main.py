from db import open_orm, close_orm, Characters, Session
from datetime import datetime
from itertools import batched
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
        await open_orm()
        client = aiohttp.ClientSession()
        async with Session() as session:
            for set_id in batched(range(101), 5):
                coros_pers = [get_person(id, client) for id in set_id]
                coros_plans = []
                for_del = []

                person = await asyncio.gather(*coros_pers)

                for i, v in enumerate(person):
                    person_data = person[i]
                    if person_data is None:
                        for_del.append(i)
                        continue
                    planet_url = person_data["homeworld"]
                    coros_plans.append(get_planet(planet_url, client))

                if for_del:
                    person = [rec for i, rec in enumerate(person) if i not in for_del]
                    set_id = [rec for i, rec in enumerate(set_id) if i not in for_del]

                planet = await asyncio.gather(*coros_plans)

                if person:
                    for per, pl, id in zip(person, planet, set_id):
                        session.add(Characters(
                            id=id,
                            birth_year=per["birth_year"],
                            eye_color=per["eye_color"],
                            gender=per["gender"],
                            hair_color=per["hair_color"],
                            homeworld=pl,
                            mass=per["mass"],
                            name=per["name"],
                            skin_color=per["skin_color"]
                        ))
                        await session.commit()

    except aiohttp.client_exceptions.ContentTypeError as err:
        raise err("Отправлено слишком большое количество запросов")
    except Exception as err:
        raise err
    finally:
        await client.close()
        await close_orm()


start = datetime.now()
asyncio.run(main())
print("Данные получены за:", datetime.now() - start)
