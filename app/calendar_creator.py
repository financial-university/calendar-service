import hashlib
from datetime import datetime
from typing import Dict, Set

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
    if now.month < 8:
        return (
            datetime(now.year, 1, 8).strftime(DATE_FORMAT),
            datetime(now.year, 6, 30).strftime(DATE_FORMAT),
        )
    else:
        return (
            datetime(now.year, 8, 15).strftime(format),
            datetime(now.year + 1, 1, 31).strftime(format),
        )


def create_calendar(rasp: list, url: str = "", exclude: set = None):
    if exclude is None:
        exclude = set()
    cal = Calendar()
    cal["version"] = "2.0"
    cal["prodid"] = "-//FU_calendar//FU calendar 1.0//RU"
    cal["method"] = "PUBLISH"
    cal["color"] = "teal"
    cal["url"] = url

    cal["x-wr-calname"] = "Расписание Университета"
    cal["DESCRIPTION"] = "Расписание Финансового Университета schedule.fa.ru"
    cal["X-WR-CALDESC"] = "Расписание Финансового Университета schedule.fa.ru"
    cal["x-wr-timezone"] = "Europe/Moscow"
    cal["TIMEZONE-ID"] = "Europe/Moscow"
    cal["X-PUBLISHED-TTL"] = "PT4H"
    cal.add("REFRESH-INTERVAL;VALUE=DURATION", "PT4H")

    tz = Timezone()
    tz["TZID"] = "Europe/Moscow"

    tzs = TimezoneStandard()
    tzs["DTSTART"] = "16010101T000000"
    tzs["TZOFFSETFROM"] = "+0300"
    tzs["TZOFFSETTO"] = "+0300"
    tz.add_component(tzs)
    cal.add_component(tz)

    date_stamp = datetime.now()

    for pair in rasp:
        if pair["disciplineOid"] in exclude:
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
            f"{pair['type']}\nПреподаватель: {pair['teachers_name']}\nГруппы: {pair['groups']}\n{note}",
        )
        event.add(
            "uid",
            f'{hashlib.md5((pair["date"].isoformat() + pair["time_start"] + pair["teachers_name"]).encode()).hexdigest()}__fu_schedule',
        )
        cal.add_component(event)

    return cal.to_ical()


async def download_calendar(id: int, type: str, params: Dict[str, Set[str]]):
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
    exclude = params.get("ex", set())
    return create_calendar(
        pairs_list, f"https://schedule.fa.ru/calendar/{type}/{id}", exclude
    )
