# coding: utf-8
import random

from questgen import exceptions

from questgen import facts


class Selector(object):
    __slots__ = ('_kb', '_qb', '_is_first_quest', '_reserved', '_excluded_quests', '_social_connection_probability')

    def __init__(self, kb, qb, social_connection_probability=0):
        self._kb = kb
        self._qb = qb
        self._social_connection_probability = social_connection_probability
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

    def new_place(self, candidates=None, terrains=None, types=None):
        places = (place for place in self._kb.filter(facts.Place) if place.uid not in self._reserved)

        if types is not None:
            places = (place for place in places if place.type in types)

        if candidates is not None:
            places = (place for place in places if place.uid in candidates)

        if terrains:
            terrains = set(terrains)
            places = (place for place in places if set(place.terrains) & terrains)

        places = list(places)

        if not places:
            raise exceptions.NoFactSelectedError(method='new_place',
                                                 arguments={'terrains': terrains,
                                                            'types': types,
                                                            'candidates': candidates},
                                                 reserved=self._reserved)

        place = random.choice(places)
        self._reserved.add(place.uid)

        return place


    def place_for(self, objects):
        locations = list(self._locations(objects=objects, restrict_places=False, restrict_objects=False))

        if not locations:
            raise exceptions.NoFactSelectedError(method='place', arguments={'objects': objects}, reserved=self._reserved)

        place = self._kb[random.choice(locations).place]

        self._reserved.add(place.uid)

        return place

    def check_social_connections(self, person, connected_person_uid, social_connection_type):
        return any(fact.person_from == person.uid and fact.person_to == connected_person_uid and fact.type == social_connection_type
                   for fact in self._kb.filter(facts.SocialConnection))

    def new_person(self,
                   first_initiator=False,
                   candidates=None,
                   professions=None,
                   places=None,
                   restrict_places=True,
                   restrict_persons=True,
                   restrict_social_connections=(),
                   social_connections=()):
        locations = self._locations(places=places, restrict_places=restrict_places, restrict_objects=restrict_persons)

        persons = (self._kb[location.object] for location in locations if isinstance(self._kb[location.object], facts.Person))

        for connected_person_uid, social_connection_type in restrict_social_connections:
            persons = (person for person in persons
                       if not self.check_social_connections(person, connected_person_uid, social_connection_type))

        social_filter_applied = False

        if social_connections:
            probability = self._social_connection_probability * len(set(connected_person_uid for connected_person_uid, social_connection_type in social_connections))
            if random.random() < probability:
                social_filter_applied = True
                persons = (person for person in persons
                           if any(self.check_social_connections(person, connected_person_uid, social_connection_type)
                                  for connected_person_uid, social_connection_type in social_connections))

        if professions is not None:
            persons = (person for person in persons if person.profession in professions)

        if candidates is not None:
            persons = (person for person in persons if person.uid in candidates)

        if first_initiator:
            not_initiators = set(restriction.person for restriction in self._kb.filter(facts.NotFirstInitiator))
            persons = (person for person in persons if person.uid not in not_initiators)

        persons = list(persons)

        if not persons:
            if social_filter_applied:
                return self.new_person(first_initiator=first_initiator,
                                       candidates=candidates,
                                       professions=professions,
                                       places=places,
                                       restrict_places=restrict_places,
                                       restrict_persons=restrict_persons,
                                       restrict_social_connections=restrict_social_connections,
                                       social_connections=()) # <- reset social connections requirements
            else:
                raise exceptions.NoFactSelectedError(method='new_person',
                                                     arguments={'first_initiator': first_initiator,
                                                                'candidates': candidates,
                                                                'professions': professions,
                                                                'places': places,
                                                                'restrict_places': restrict_places,
                                                                'restrict_persons': restrict_persons},
                                                     reserved=self._reserved)

        person = random.choice(persons)
        self._reserved.add(person.uid)

        return person

    def preferences_mob(self):
        try:
            return next(self._kb.filter(facts.PreferenceMob))
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_mob', arguments={}, reserved=self._reserved)

    def preferences_hometown(self):
        try:
            return next(self._kb.filter(facts.PreferenceHometown))
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_hometown', arguments={}, reserved=self._reserved)

    def preferences_enemy(self):
        try:
            return next(self._kb.filter(facts.PreferenceEnemy))
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_enemy', arguments={}, reserved=self._reserved)

    def preferences_friend(self):
        try:
            return next(self._kb.filter(facts.PreferenceFriend))
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='preferences_friend', arguments={}, reserved=self._reserved)

    def upgrade_equipment_cost(self):
        try:
            return next(self._kb.filter(facts.UpgradeEquipmentCost))
        except StopIteration:
            raise exceptions.NoFactSelectedError(method='upgrade_equipment_cost', arguments={}, reserved=self._reserved)

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
