import hashlib
from datetime import datetime
from functools import lru_cache

import pytz
from aiohttp import ClientSession, ClientError
from icalendar import Calendar, Event, Timezone, TimezoneStandard

DATE_FORMAT = "%Y.%m.%d"


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
    cal["x-wr-calname"] = "Расписание Университета"
    cal["x-wr-timezone"] = "Europe/Moscow"

    tz = Timezone()
    tz['TZID'] = 'Europe/Moscow'
    cal.add_component(tz)

    tzs = TimezoneStandard()
    tzs['DTSTART'] = '16010101T000000'
    tzs['TZOFFSETFROM'] = '+0300'
    tzs['TZOFFSETTO'] = '+0300'
    cal.add_component(tzs)

    date_stamp = datetime.now()

    for pair in rasp:
        if pair["discipline"] == "Военная подготовка":
            continue
        event = Event()
        event.add("summary", pair["discipline"])
        date = datetime.strptime(pair["date"], DATE_FORMAT)
        event.add(
            "dtstart",
            datetime(
                date.year,
                date.month,
                date.day,
                *map(int, pair["beginLesson"].split(":")),
                tzinfo=pytz.timezone("Europe/Moscow"),
            ),
        )
        event.add(
            "dtend",
            datetime(
                date.year,
                date.month,
                date.day,
                *map(int, pair["endLesson"].split(":")),
                tzinfo=pytz.timezone("Europe/Moscow"),
            ),
        )
        event.add("dtstamp", date_stamp)
        event.add(
            "location", f"{pair['auditorium'].split('/')[-1]}, {pair['building']}"
        )
        event.add(
            "description",
            f"{pair['kindOfWork']}\nПреподователь: {pair['lecturer']}\nГруппы: {pair['group'] or pair['stream']}",
        )
        event.add(
            "uid",
            f'{hashlib.md5((pair["date"] + pair["beginLesson"] + pair["lecturer"]).encode()).hexdigest()}__fu_schedule',
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
                pairs_list = await request.json()
                if not pairs_list:
                    raise EmptySchedule()
        except ClientError:
            raise ServiceUnavailable()
    return create_calendar(pairs_list)
