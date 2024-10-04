#!/usr/bin/env python3
import csv
import io
import json
import re
import statistics
import sys

import requests
from pyquery import PyQuery as pq
from dataclasses import dataclass
import typing
from datetime import datetime
from enum import Enum


class Event(Enum):
    THREE = '333'
    TWO = '222'
    FOUR = '444'
    FIVE = '555'
    SIX = '666'
    THREE_BLIND_FOLD = '333bf'
    THREE_ONE_HAND = '333oh'
    CLOCK = 'clock'
    MEGAMINX = 'minx'
    PYRAMINX = 'pyram'
    SKEWB = 'skewb'
    SQUARE_ONE = 'sq1'

    @classmethod
    def parse(cls, value: str) -> any:
        try:
            return cls(value)
        except ValueError:
            return value

    def __str__(self):
        return self.value

    def __lt__(self, other: 'Event'):
        return self.value.__lt__(other.value)


@dataclass
class Competition:
    DATE_FORMAT = '%Y/%m/%d'
    identifier: str
    name: str
    location: str
    venue: str
    date: datetime
    link: str

    def __str__(self):
        return '[{}] {} ({})'.format(self.date.strftime(self.DATE_FORMAT), self.name, self.identifier)

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other: 'Competition'):
        if self.date == other.date:
            return self.name.__lt__(other.name)

        return self.date.__lt__(other.date)


@dataclass
class Person:
    name: str
    identifier: typing.Optional[str] = None
    ranks: typing.Optional[typing.Dict[str, int]] = None
    averages: typing.Optional[typing.Dict[str, float]] = None
    country: typing.Optional[str] = None
    link: typing.Optional[str] = None

    @property
    def rank(self) -> int:
        if self.ranks:
            return sorted(self.ranks.values())[0]

        return sys.maxsize

    def __str__(self):
        if self.ranks:
            return '------------------------------------\n[Rank {}] {} ({})\n------------------------------------\n{}'.format(self.rank, self.name, self.identifier, '\n'.join(['[{}]\t: {} (Rank {})'.format(event, self.averages[event], self.ranks[event]) for event in sorted(self.averages.keys())]))

        if self.identifier:
            return '{} ({})'.format(self.name, self.identifier)

        return self.name

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other: 'Person'):
        if self.rank == other.rank:
            return self.name.__lt__(other.name)

        return self.rank < other.rank


class WCA:
    _location_cleanup = re.compile('<[|/]strong>')
    _date_cleanup = re.compile('<i[ |>][^>]+></i>')
    _date_format = '%b %d, %Y'
    _person_country_cleanup = re.compile('<span[ |>][^>]+></span>')

    def __init__(self, host: str = 'https://www.worldcubeassociation.org'):
        self.host = host

    def list_competitions(self, search: str = '') -> typing.List[Competition]:
        url = '{}/competitions'.format(self.host)
        if search:
            url = url + '?search={}'.format(search)

        res = requests.get(url)
        doc = pq(res.content)

        blocks = doc('#search-results .competition-info').items()
        competitions = []  # type: typing.List[Competition]
        for block in blocks:  # type: pq
            anchor = block('.competition-link a')  # type: pq
            link = anchor.attr('href')
            identifier = link.split('/')[-1]
            name = anchor.text()
            location = self._location_cleanup.sub('', block('.location').text())
            venue = block('.venue-link p').text()

            date = self._date_cleanup.sub('', block.parent()('.date').text())
            date = datetime.strptime(date, self._date_format)

            competitions.append(Competition(
                identifier=identifier,
                name=name,
                location=location,
                venue=venue,
                date=date,
                link=link,
            ))

        return competitions

    def get_person(self, identifier: str) -> Person:
        res = requests.get('{}/persons/{}'.format(self.host, identifier))
        doc = pq(res.content)

        name = doc('title').text().split('|')[0].strip()

        profile = doc('#person')
        country = self._person_country_cleanup.sub('', profile('country').text()).strip()
        ranks = dict()
        averages = dict()
        
        records = doc('.personal-records tr').items()
        for record in records:  # type: pq
            cells = record('td').items()
            record_event = ''
            event_rank = sys.maxsize
            event_average = float(sys.maxsize)

            for cell in cells:  # type: pq
                if not record_event:
                    event = cell.attr('data-event')
                    if event:
                        record_event = Event.parse(event)

                if cell.has_class('world-rank'):
                    for o in cell('.world-rank').items():
                        txt = o.text()
                        if len(txt) > 0:
                            if event_rank > int(txt):
                                event_rank = int(txt)

                if cell.has_class('average'):
                    average = cell('.average a').text().strip()
                    segs = [a for a in average.split(':') if a]
                    minutes = 0
                    seconds = 0.0
                    if len(segs) == 2:
                        minutes = int(segs[0])
                        seconds = float(segs[-1])
                    elif len(segs) == 1:
                        seconds = float(segs[0])

                    event_average = minutes * 60 + seconds

            if record_event:
                ranks[record_event] = event_rank
                averages[record_event] = event_average

        return Person(
            identifier=identifier,
            name=name,
            country=country,
            ranks=ranks,
            averages=averages,
            link='/persons/{}'.format(identifier),
        )

    def list_competitors(self, competition_id: str) -> typing.List[Person]:
        res = requests.get('{}/competitions/{}/registrations'.format(self.host, competition_id))
        doc = pq(res.content)

        blocks = doc('#competition-data table tbody tr').items()

        competitors = []  # type: typing.List[Person]
        for block in blocks:  # type: pq
            name_block = block('.name')
            anchor = name_block('a')  # type: pq
            if anchor:
                link = anchor.attr('href')
                identifier = link.split('/')[-1]
                name = anchor.text()
            else:
                identifier = ''
                name = name_block.text()

            competitors.append(Person(
                identifier=identifier,
                name=name,
            ))

        return competitors


if __name__ == '__main__':

    class CLIEncoder(json.JSONEncoder):
        def default(self, o: typing.Any):
            if isinstance(o, (Competition, Person)):
                return o.__dict__
            elif isinstance(o, datetime):
                return o.strftime(Competition.DATE_FORMAT)

            return json.JSONEncoder.default(self, o)


    def format_object(obj, separator: str = ', '):
        if isinstance(obj, (set, list, tuple)):
            return separator.join([format_object(o) for o in list(obj)])
        elif isinstance(obj, dict):
            return separator.join('{}: {}'.format(k, v) for k, v in obj.items())
        elif isinstance(obj, (Competition, Person)):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.strftime(Competition.DATE_FORMAT)

        return obj


    def format_result(result, format_: str) -> str:
        if format_ == 'short':
            return format_object(result, separator='\n')

        if format_ == 'csv':
            if not isinstance(result, list):
                return format_object(result)
            if len(result) == 0:
                return ''

            out = io.StringIO()
            writer = csv.DictWriter(out, list(result[0].keys()), quoting=csv.QUOTE_NONNUMERIC)

            writer.writeheader()

            for row in result:
                writer.writerow(row)

            return out.getvalue()
        else:
            return json.dumps(result, cls=CLIEncoder, indent=2, sort_keys=True)

    def get_stats(nums: typing.Iterable) -> dict:
        if not nums:
            return {}

        return {
            'min': min(nums),
            'max': max(nums),
            'mean': statistics.mean(nums),
            '25p': statistics.quantiles(nums, n=100)[24],
            'median': statistics.median(nums),
            '75p': statistics.quantiles(nums, n=100)[74],
            '95p': statistics.quantiles(nums, n=100)[95],
            '99p': statistics.quantiles(nums, n=100)[98],
        }

    def main():
        from argparse import ArgumentParser
        import concurrent.futures
        import statistics

        parser = ArgumentParser(description='World Cube Association CLI')
        parser.add_argument('--format', '-f', default='short', choices=('short', 'csv', 'json'), help='format')
        parser.add_argument('--concurrency', '-c', type=int, default=8, help='remote call concurrency')

        command_parser = parser.add_subparsers(dest='command')
        command_competitions = command_parser.add_parser('competitions')
        command_competitions.add_argument('--search', '-s', type=str, help='search keywords')

        command_competitors = command_parser.add_parser('competitors')
        command_competitors.add_argument('competition_id', type=str, help='Competition ID')

        command_competitors = command_parser.add_parser('competitor-stats')
        command_competitors.add_argument('competition_id', type=str, help='Competition ID')
        command_competitors.add_argument('--event', type=str, default=Event.THREE.value, choices=[
            e.value for e in Event
        ], help='display average time stats for the given event')

        command_person = command_parser.add_parser('person')
        command_person.add_argument('person_id', type=str, help='Person ID')

        args = parser.parse_args()

        wca = WCA()

        if args.command == 'competitions':
            res = wca.list_competitions(args.search)
        elif args.command == 'competitors':
            res = wca.list_competitors(args.competition_id)
        elif args.command == 'competitor-stats':
            event = Event.parse(args.event)
            persons = wca.list_competitors(args.competition_id)
            ids = [person.identifier for person in persons if person.identifier]

            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                results = executor.map(wca.get_person, ids)

            res = get_stats([person.averages[event] for person in results if event in person.averages])
        elif args.command == 'person':
            res = wca.get_person(args.person_id)
        else:
            parser.print_help()
            exit(1)

        print(format_result(res, args.format))

    main()
