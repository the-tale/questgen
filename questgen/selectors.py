# coding: utf-8
import random

from questgen import exceptions

from questgen import facts


class Selector(object):

    def __init__(self, kb):
        self._kb = kb
        self._reserved = set()

    def _locations(self, restrict_places, restrict_objects, objects=None, places=None):
        locations = self._kb.filter(facts.LocatedIn)

        if restrict_places:
            locations = (location for location in locations if location.place not in self._reserved)

        if restrict_objects:
            locations = (location for location in locations if location.object not in self._reserved)

        if objects is not None:
            locations = (location for location in locations if location.object in objects)

        if places is not None:
            locations = (location for location in locations if location.place in places)

        return locations

    def heroes(self): return list(self._kb.filter(facts.Hero))

    def new_place(self):
        places = [place for place in self._kb.filter(facts.Place) if place.uid not in self._reserved]

        if not places:
            raise exceptions.NoFactSelectedError(method='new_place', arguments=None)

        place_uid = random.choice(places).uid
        self._reserved.add(place_uid)

        return place_uid


    def place_for(self, objects):
        locations = list(self._locations(objects=objects, restrict_places=False, restrict_objects=False))

        if not locations:
            raise exceptions.NoFactSelectedError(method='place', arguments={'objects': objects})

        place_uid = random.choice(locations).place

        self._reserved.add(place_uid)

        return place_uid

    def new_person(self):
        locations = self._locations(restrict_places=True, restrict_objects=True)
        persons = list(location.object for location in locations if isinstance(self._kb[location.object], facts.Person))

        if not persons:
            raise exceptions.NoFactSelectedError(method='new_person', arguments=None)

        person_uid = random.choice(persons)
        self._reserved.add(person_uid)

        return person_uid

    def person_from(self, places):
        locations = self._locations(places=places, restrict_places=False, restrict_objects=False)

        persons = list(location.object for location in locations if isinstance(self._kb[location.object], facts.Person))

        if not persons:
            raise exceptions.NoFactSelectedError(method='person_from', arguments={'places': places})

        person_uid = random.choice(persons)

        self._reserved.add(person_uid)

        return person_uid
