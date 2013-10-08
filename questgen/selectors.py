# coding: utf-8
import random

from questgen import exceptions

from questgen import facts


class Selector(object):

    def __init__(self, kb, qb):
        self._kb = kb
        self._qb = qb
        self.reset()

    def reset(self):
        self._reserved = set()
        self._is_first_quest = True
        self._excluded_quests = set()

    @property
    def is_first_quest(self):
        if self._is_first_quest:
            self._is_first_quest = False
            return True
        return False

    def reserve(self, fact):
        self._reserved.add(fact.uid)

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

    def heroes(self): return list(h for h in self._kb.filter(facts.Hero))

    def new_place(self, candidates=None, terrains=None):
        places = (place for place in self._kb.filter(facts.Place) if place.uid not in self._reserved)

        if candidates is not None:
            places = (place for place in places if place.uid in candidates)

        if terrains:
            terrains = set(terrains)
            places = (place for place in places if set(place.terrains) & terrains)

        places = list(places)

        if not places:
            raise exceptions.NoFactSelectedError(method='new_place', arguments={'terrains': terrains})

        place = random.choice(places)
        self._reserved.add(place.uid)

        return place


    def place_for(self, objects):
        locations = list(self._locations(objects=objects, restrict_places=False, restrict_objects=False))

        if not locations:
            raise exceptions.NoFactSelectedError(method='place', arguments={'objects': objects})

        place = self._kb[random.choice(locations).place]

        self._reserved.add(place.uid)

        return place

    def new_person(self, candidates=None, professions=None):
        locations = self._locations(restrict_places=True, restrict_objects=True)
        persons = (self._kb[location.object] for location in locations if isinstance(self._kb[location.object], facts.Person))

        if professions is not None:
            persons = (person for person in persons if person.profession in professions)

        if candidates is not None:
            persons = (person for person in persons if person.uid in candidates)

        persons = list(persons)

        if not persons:
            raise exceptions.NoFactSelectedError(method='new_person', arguments=None)

        person = random.choice(persons)
        self._reserved.add(person.uid)

        return person

    def person_from(self, places):
        locations = self._locations(places=places, restrict_places=False, restrict_objects=False)

        persons = list(location.object for location in locations if isinstance(self._kb[location.object], facts.Person))

        if not persons:
            raise exceptions.NoFactSelectedError(method='person_from', arguments={'places': places})

        person = self._kb[random.choice(persons)]

        self._reserved.add(person.uid)

        return person

    def preferences_mob(self):
        try:
            return self._kb.filter(facts.PreferenceMob).next()
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_mob', arguments={})

    def preferences_hometown(self):
        try:
            return self._kb.filter(facts.PreferenceHometown).next()
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_hometown', arguments={})

    def preferences_enemy(self):
        try:
            return self._kb.filter(facts.PreferenceEnemy).next()
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_enemy', arguments={})

    def preferences_friend(self):
        try:
            return self._kb.filter(facts.PreferenceFriend).next()
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_friend', arguments={})


    def create_quest_from_place(self, nesting, initiator_position, **kwargs):
        excluded = set(kwargs.get('excluded', []))
        excluded |= self._excluded_quests
        kwargs['excluded'] = excluded

        quest_class = self._qb.quest_from_place(**kwargs)
        if 'has_subquests' in quest_class.TAGS:
            self._excluded_quests.add(quest_class.TYPE)

        return quest_class.construct_from_place(nesting=nesting, selector=self, start_place=initiator_position)

    def create_quest_from_person(self, nesting, initiator, **kwargs):
        excluded = set(kwargs.get('excluded', []))
        excluded |= self._excluded_quests
        kwargs['excluded'] = excluded

        quest_class = self._qb.quest_from_person(**kwargs)
        if 'has_subquests' in quest_class.TAGS:
            self._excluded_quests.add(quest_class.TYPE)

        return quest_class.construct_from_person(nesting=nesting, selector=self, initiator=initiator)

    def create_quest_between_2(self, nesting, initiator, receiver, **kwargs):
        excluded = set(kwargs.get('excluded', []))
        excluded |= self._excluded_quests
        kwargs['excluded'] = excluded

        quest_class = self._qb.quest_between_2(**kwargs)

        if 'has_subquests' in quest_class.TAGS:
            self._excluded_quests.add(quest_class.TYPE)

        return quest_class.construct_between_2(nesting=nesting, selector=self, initiator=initiator, receiver=receiver)
