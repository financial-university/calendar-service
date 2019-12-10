import hashlib
from datetime import datetime

import pytz
from icalendar import Calendar, Event

DATE_FORMAT = '%Y.%m.%d'


def create_calendar(rasp: list):
    cal = Calendar()
    cal['version'] = '2.0'
    cal['prodid'] = '-//FU_calendar//FU calendar 1.0//RU'
    cal['method'] = 'PUBLISH'
    cal['x-wr-calname'] = 'Расписание Университета'
    cal['x-wr-timezone'] = 'Europe/Moscow'
    date_stamp = datetime.now()

    for pair in rasp:
        event = Event()
        event.add('summary', pair['discipline'])
        date = datetime.strptime(pair['date'], DATE_FORMAT)
        event.add('dtstart', datetime(date.year, date.month, date.day, *map(int, pair['beginLesson'].split(':')),
                                      tzinfo=pytz.timezone("Europe/Moscow")))
        event.add('dtend', datetime(date.year, date.month, date.day, *map(int, pair['endLesson'].split(':')),
                                    tzinfo=pytz.timezone("Europe/Moscow")))
        event.add('dtstamp', date_stamp)
        event.add('location', f"{pair['auditorium'].split('/')[-1]}, {pair['building']}")
        event.add('description',
                  f"{pair['kindOfWork']}\nПреподователь: {pair['lecturer']}\nГруппы: {pair['group'] or pair['stream']}")
        event.add('uid',
                  f'{hashlib.md5((pair["date"] + pair["beginLesson"]).encode()).hexdigest()}__fu_schedule')
        cal.add_component(event)

    return cal.to_ical()
