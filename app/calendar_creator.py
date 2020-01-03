import hashlib
from datetime import datetime
from functools import lru_cache

from aiohttp import ClientSession, ClientError
from icalendar import Calendar, Event, Timezone, TimezoneStandard
import pytz
from ujson import loads

from app.schemas import Pair

DATE_FORMAT = "%Y.%m.%d"
PAIR_SCHEMA = Pair()


class EmptySchedule(Exception):
    pass


class ServiceUnavailable(Exception):
    pass


def get_dates():
    now = datetime.now()
    format = "%Y.%m.%d"
    if now.month < 8:
        return (
            datetime(now.year, 1, 8).strftime(format),
            datetime(now.year, 6, 30).strftime(format),
        )
    else:
        return (
            datetime(now.year, 8, 15).strftime(format),
            datetime(now.year + 1, 1, 31).strftime(format),
        )


def create_calendar(rasp: list):
    cal = Calendar()
    cal["version"] = "2.0"
    cal["prodid"] = "-//FU_calendar//FU calendar 1.0//RU"
    cal["method"] = "PUBLISH"
    cal["color"] = "teal"
    cal["x-wr-calname"] = "Расписание Университета"
    cal["x-wr-timezone"] = "Europe/Moscow"

    tz = Timezone()
    tz["TZID"] = "Europe/Moscow"
    cal.add_component(tz)

    tzs = TimezoneStandard()
    tzs["DTSTART"] = "16010101T000000"
    tzs["TZOFFSETFROM"] = "+0300"
    tzs["TZOFFSETTO"] = "+0300"
    cal.add_component(tzs)

    date_stamp = datetime.now()

    for pair in rasp:
        if pair["discipline"] == "Военная подготовка":
            continue
        pair = PAIR_SCHEMA.load(pair)
        event = Event()
        event.add("summary", pair["name"])
        date = pair["date"]
        event.add(
            "dtstart",
            datetime(
                date.year,
                date.month,
                date.day,
                *map(int, pair["time_start"].split(":")),
                tzinfo=pytz.timezone("Europe/Moscow"),
            ),
        )
        event.add(
            "dtend",
            datetime(
                date.year,
                date.month,
                date.day,
                *map(int, pair["time_end"].split(":")),
                tzinfo=pytz.timezone("Europe/Moscow"),
            ),
        )
        event.add("dtstamp", date_stamp)
        event.add(
            "location", f"{pair['audience']}, {pair['location']}",
        )
        note = f'Примечание: {pair["note"]}' if pair["note"] else ""
        event.add(
            "description",
            f"{pair['type']}\nПреподователь: {pair['teachers_name']}\nГруппы: {pair['groups']}\n{note}",
        )
        event.add(
            "uid",
            f'{hashlib.md5((pair["date"].isoformat() + pair["time_start"] + pair["teachers_name"]).encode()).hexdigest()}__fu_schedule',
        )
        cal.add_component(event)

    return cal.to_ical()


async def download_calendar(id: int, type: str):
    date_start, date_end = get_dates()
    async with ClientSession() as client:
        try:
            async with client.get(
                f"http://ruz.fa.ru/api/schedule/{type}/{id}?start={date_start}&finish={date_end}&lng=1"
            ) as request:
                pairs_list = await request.json(loads=loads)
                # if not pairs_list:
                #     raise EmptySchedule()
        except ClientError:
            raise ServiceUnavailable()
    return create_calendar(pairs_list)
