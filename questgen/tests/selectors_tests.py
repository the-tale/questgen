# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen import facts
from questgen import selectors
from questgen import exceptions


class SelectordsTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

        self.kb += [ facts.Hero(uid='hero'),
                     facts.Hero(uid='hero_2'),

                     facts.Place(uid='place_1', terrains=(1,)),
                     facts.Place(uid='place_2', terrains=(0,)),
                     facts.Place(uid='place_3', terrains=(0,)),

                     facts.Person(uid='person_1', profession=0),
                     facts.Person(uid='person_2', profession=1),
                     facts.Person(uid='person_3', profession=2),

                     facts.LocatedIn(object='person_1', place='place_1'),
                     facts.LocatedIn(object='person_2', place='place_2'),
                     facts.LocatedIn(object='person_3', place='place_3'),

                     facts.Mob(uid='mob_1', terrains=(0,))]

        self.selector = selectors.Selector(self.kb, None)

    def test_heroes(self):
        self.assertEqual(set(h.uid for h in self.selector.heroes()), set(['hero','hero_2']))


    def test_new_place(self):
        for i in xrange(100):
            places = [self.selector.new_place().uid,
                      self.selector.new_place().uid,
                      self.selector.new_place().uid,]

            self.assertEqual(set(places), set(['place_1', 'place_2', 'place_3']))

            self.selector.reset()

    def test_new_place__not_found_exception(self):
        self.selector.new_place()
        self.selector.new_place()
        self.selector.new_place()

        self.assertRaises(exceptions.NoFactSelectedError, self.selector.new_place)

    def test_new_place__terrains(self):
        self.assertRaises(exceptions.NoFactSelectedError, self.selector.new_place, terrains=[2])
        self.assertEqual(self.selector.new_place(terrains=[1]).uid, 'place_1')
        self.assertTrue(self.selector.new_place(terrains=[0]).uid in ['place_2', 'place_3'])

    def test_new_place__candidates(self):
        self.assertRaises(exceptions.NoFactSelectedError, self.selector.new_place, candidates=())
        self.assertEqual(self.selector.new_place(candidates=['place_1']).uid, 'place_1')
        self.assertTrue(self.selector.new_place(candidates=['place_2', 'place_3']).uid in ['place_2', 'place_3'])

    def test_place_for(self):
        self.assertEqual(self.selector._reserved, set())

        self.assertEqual(self.selector.place_for(objects=['person_1']).uid, 'place_1')
        self.assertEqual(self.selector.place_for(objects=['person_2']).uid, 'place_2')
        self.assertEqual(self.selector.place_for(objects=['person_2']).uid, 'place_2')
        self.assertEqual(self.selector.place_for(objects=['person_3']).uid, 'place_3')

        self.assertEqual(self.selector._reserved, set(['place_1', 'place_2', 'place_3']))

    def test_place_for__no_place(self):
        self.assertRaises(exceptions.NoFactSelectedError, self.selector.place_for, objects=['person_666'])
        self.assertEqual(self.selector._reserved, set())


    def test_new_person(self):
        for i in xrange(100):
            persons = [self.selector.new_person().uid,
                      self.selector.new_person().uid,
                      self.selector.new_person().uid,]

            self.assertEqual(set(persons), set(['person_1', 'person_2', 'person_3']))

            self.selector.reset()

    def test_new_person__profession(self):
        for i in xrange(100):
            persons = [self.selector.new_person(professions=(0, 2)).uid,
                      self.selector.new_person(professions=(0, 2)).uid]

            self.assertEqual(set(persons), set(['person_1', 'person_3']))

            self.selector.reset()


    def test_new_person__not_found_exception(self):
        self.selector.new_person()
        self.selector.new_person()
        self.selector.new_person()

        self.assertRaises(exceptions.NoFactSelectedError, self.selector.new_person)


    def test_person_from(self):
        self.assertEqual(self.selector._reserved, set())

        self.assertEqual(self.selector.person_from(places=['place_1']).uid, 'person_1')
        self.assertEqual(self.selector.person_from(places=['place_2']).uid, 'person_2')
        self.assertEqual(self.selector.person_from(places=['place_2']).uid, 'person_2')
        self.assertEqual(self.selector.person_from(places=['place_3']).uid, 'person_3')

        self.assertEqual(self.selector._reserved, set(['person_1', 'person_2', 'person_3']))

    def test_person_from__no_person(self):
        self.assertRaises(exceptions.NoFactSelectedError, self.selector.person_from, places=['place_666'])
        self.assertEqual(self.selector._reserved, set())


    def test_preferences_mob(self):
        self.kb += facts.PreferenceMob(object='hero', mob='mob_1')
        self.assertEqual(self.selector.preferences_mob(), facts.PreferenceMob(object='hero', mob='mob_1'))

    def test_preferences_mob__not_found(self):
        self.assertRaises(exceptions.NoFactSelectedError, self.selector.preferences_mob)

    def test_preferences_hometown(self):
        self.kb += facts.PreferenceHometown(object='hero', place='place_2')
        self.assertEqual(self.selector.preferences_hometown(), facts.PreferenceHometown(object='hero', place='place_2'))

    def test_preferences_hometown__not_found(self):
        self.assertRaises(exceptions.NoFactSelectedError, self.selector.preferences_hometown)
