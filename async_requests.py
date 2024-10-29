import asyncio

import aiohttp
from more_itertools import chunked

from models import Session, SwapiPeople, init_orm

MAX_REQUEST = 15

async def fetch_data(url, http_session, field_name):
    response = await http_session.get(url)
    if response.status == 200:
        json_data = await response.json()
        return json_data.get(field_name)
    return None

async def get_people(person_id, http_session):

    response = await http_session.get(f"https://swapi.py4e.com/api/people/{person_id}/")
    json_data = await response.json()
    if json_data.get("detail") == "Not found":
            print(f"Данные для {person_id} не найдены")
            return None

    tasks = {
        "homeworld": fetch_data(json_data.get("homeworld"), http_session, "name") if json_data.get(
            "homeworld") else None,
        "films": asyncio.gather(*(fetch_data(url, http_session, "title") for url in json_data.get("films", []))),
        "species": asyncio.gather(*(fetch_data(url, http_session, "name") for url in json_data.get("species", []))),
        "starships": asyncio.gather(*(fetch_data(url, http_session, "name") for url in json_data.get("starships", []))),
        "vehicles": asyncio.gather(*(fetch_data(url, http_session, "name") for url in json_data.get("vehicles", []))),
    }
    results = await asyncio.gather(*tasks.values())

    json_data.update({
        "homeworld": results[0],
        "films": results[1],
        "species": results[2],
        "starships": results[3],
        "vehicles": results[4],
    })

    return json_data


async def insert(jsons_list):
    async with Session() as db_session:
        orm_objects = []
        for json_item in jsons_list:
            if json_item is None:
                continue
            orm_objects.append(SwapiPeople(
                name=json_item.get("name"),
                height=json_item.get("height"),
                mass=json_item.get("mass"),
                hair_color=json_item.get("hair_color"),
                skin_color=json_item.get("skin_color"),
                eye_color=json_item.get("eye_color"),
                birth_year=json_item.get("birth_year"),
                gender=json_item.get("gender"),
                homeworld=json_item.get("homeworld"),
                films=", ".join(json_item.get("films", [])),
                species=", ".join(json_item.get("species", [])),
                starships=", ".join(json_item.get("starships", [])),
                vehicles=", ".join(json_item.get("vehicles", []))
            ))
        db_session.add_all(orm_objects)
        await db_session.commit()


async def main():
    await init_orm()
    async with aiohttp.ClientSession() as http_session:
        for people_id_chunk in chunked(range(1, 89), MAX_REQUEST):
            if await get_people(people_id_chunk[0], http_session) is None:
                continue
            coros = [get_people(i, http_session) for i in people_id_chunk]
            jsons_list = await asyncio.gather(*coros)
            task = asyncio.create_task(insert(jsons_list))
    tasks_set = asyncio.all_tasks()
    current_task = asyncio.current_task()
    tasks_set.remove(current_task)
    await asyncio.gather(*tasks_set)


asyncio.run(main())
