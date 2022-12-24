import csv

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from apps.models import CustomUser, Region, District


class Command(BaseCommand):
    help = 'Adding csv file to database if with this name is exist.'

    def add_arguments(self, parser):
        parser.add_argument('type', type=str, help='This is name of database.')
        parser.add_argument('url', type=str, help='This is url of csv file.')


    def handle(self, *args, **kwargs):
        _type = kwargs['type']
        url = kwargs['url']
        try:
            with open(url, 'r') as file:
                file.readline()
                csvreader = csv.reader(file)
                if _type in 'regions':
                    for row in csvreader:
                        Region.objects.get_or_create(
                            id=row[0],
                            name=row[1]
                        )
                        print(row[1], ' added')
                elif _type in 'districts':
                    for row in csvreader:
                        try:
                            District.objects.get_or_create(
                                id = row[0],
                                name=row[1],
                                region_id=row[2]
                            )
                            print(f'{row[1]} added')
                        except ValueError:
                            print(f'this region name={row[1]} id={row[2]} is not exist')

        except FileNotFoundError:
            return f'No such file {url}'
