import csv
from datetime import datetime
import locale
import logging
from functools import reduce
from random import shuffle
import argparse

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

locale.setlocale(locale.LC_ALL, "fr")


class Person:   # defines attributes of a person
    def __init__(self, elements):
        self.name = elements[0]
        self.email = elements[1]
        self.licence = True if elements[2] == "1" else False
        self.choices = [x.split(' - ') for x in elements[3].split(',')]
        self.choices = [Event(datetime.strptime(x[0]+'/19' if len(x[0]) < 6 else x[0], '%d/%m/%y'), x[1])
                        for x in self.choices]   # make datetime, adds year if date is only DD/MM
        self.count = 0  # number of times a person has helped

    def __str__(self):
        return '%s (%s)' % (self.name, self.email)

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_choices(self):
        return self.choices

    def get_count(self):
        return self.count

    def add_count(self):    # add to the time a person has helped
        self.count += 1


class Event:    # Event (Ferme ou Tri)
    def __init__(self, dt, description):
        self.dt = dt.date()
        self.description = description
        self.availability = 0
        self.persons = []

    def get_dt(self):
        return self.dt

    def get_description(self):
        return self.description

    def get_availability(self):
        return self.availability

    def increment_av(self):
        self.availability += 1

    def add_person(self, person: Person):
        self.persons.append(person)

    def get_persons(self):
        return self.persons

    def __str__(self):
        return "%s @ %s (available: %s)\nVolunteers:\n\t%s"\
               % (self.description, self.dt.strftime('%d/%m'), self.availability, '\n\t'.join([str(x) for x in self.get_persons()]))

    def __lt__(self, other):
        return self.dt < other.dt

    def __le__(self, other):
        return self.dt < other.dt

    def __eq__(self, other):
        return self.dt == other.dt and self.description == other.description


class Plan:
    def __init__(self, person_list):
        self.person_list = person_list
        self.events = []
        for person in self.person_list:     # to extract covered dates
            self.events += [event for event in person.choices if event not in self.events]
        self.events = sorted(self.events)
        for event in self.events:       # get number of available people for all dates
            for person in self.person_list:
                if event in person.choices:
                    event.increment_av()
        self.events.sort(key=lambda x: x.get_availability())    # sort for event with the least people aviable first
        for event in self.events:
            shuffle(self.person_list)   # randomize people list, equalizes chance to be attributed to a job
            self.person_list.sort(key=lambda x: x.get_count())  # order randomized list by aviability of people, so
                                                                # people with little aviability are picked fist
            if event.get_availability() < 2:                    # check if event has enough aviable volunteers
                logging.debug('Event "%s" has not enough available volunteers.' % event)
            for person in self.person_list:     # adds persons to events
                if self.check_if_person_suitable(person, event):
                    event.add_person(person)
                    person.add_count()
                    logging.debug('\n\tAdded %s to %s' % (person, event))
                if len(event.get_persons()) == 2 and event.get_description() == 'Ferme' \
                        or len(event.get_persons()) == 4 and event.get_description() == 'Tri':
                    logging.debug('Event "%s" full.' % event)
                    break
        self.events.sort(key=lambda x: x.get_description())
        self.events.sort(key=lambda x: x.get_dt())

    def check_if_person_suitable(self, check_person, check_event):
        flag = False
        if check_person.get_count() <= self.get_average_count() and check_event in check_person.get_choices():
            flag = True
        for event in self.events:
            for person in event.get_persons():
                if person == check_person and event.get_dt() == check_event.get_dt():
                    flag = False
        return flag

    def __str__(self):
        return 'Event list:\n%s' % ('\n'.join([str(x) for x in self.events]))

    def get_person_list(self):
        return self.person_list

    def get_average_count(self):
        return reduce(lambda x, y: x+y, [x.get_count() for x in self.get_person_list()])

    def export_csv(self, directory):
        with open(directory + r'\planning_%s.csv' % (datetime.now().strftime('%d_%m_%Y')), 'w', encoding='utf-8', newline='\n') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"')
            for event in self.events:
                writer.writerow([event.get_dt()]+[event.get_description()]+[event.get_availability()]
                                +[', '.join([str(person) for person in event.get_persons()])]
                                +[', '.join([str(person) for person in self.get_person_list()
                                             if event in person.choices and person not in event.get_persons()])])


def parser(file):
    volunteers = []
    with open(file, newline='\n', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')
        for person in reader:
            volunteers.append(Person(person)) if len(person[-1]) > 0 else None
    return volunteers


def init_parser():
    description = 'makes planning for achats solidaires'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-f', '--file', help="souce csv", required=True, type=str)
    parser.add_argument('-d', '--directory', help="where to store new csv", required=True, type=str)

    return parser.parse_args()


if __name__ == '__main__':
    logging.debug("Start of logging")
    parse = init_parser()
    volunteer_list = parser(parse.file)
    plan = Plan(volunteer_list)
    plan.export_csv(parse.directory)
