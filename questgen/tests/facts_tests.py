# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen import exceptions
from questgen import facts
from questgen import actions
from questgen import requirements


class FactsTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()


    def test_short_serialization(self):
        fact = facts.State(uid='state-uid',
                           description='some description',
                           # externals settuped to default
                           require=[requirements.IsAlive(object='hero')],
                           actions=[actions.Message(type='message-type')])
        self.assertEqual(fact.serialize(short=True), facts.State.deserialize(fact.serialize(short=True)).serialize())
        self.assertFalse('description' in fact.serialize(short=True)['attributes'])

    def test_full_serialization(self):
        fact = facts.State(uid='state-uid',
                           description='some description',
                           # externals settuped to default
                           require=[requirements.IsAlive(object='hero')],
                           actions=[actions.Message(type='message-type')])
        self.assertEqual(fact.serialize(), facts.State.deserialize(fact.serialize()).serialize())
        self.assertTrue('description' in fact.serialize()['attributes'])

    def test_check(self):
        fact = facts.Fact(uid='fact_uid')
        self.assertFalse(fact.check(self.kb))
        self.kb += fact
        self.assertTrue(fact.check(self.kb))

    def test_change(self):
        fact_1 = facts.LocatedIn(object='person_1', place='place_1')
        fact_2 = fact_1.change(place='place_2')
        self.assertEqual(fact_2.object, 'person_1')
        self.assertEqual(fact_2.place, 'place_2')

    def test_change__wrong_change_attribute(self):
        fact_1 = facts.LocatedIn(object='person_1', place='place_1')
        self.assertRaises(exceptions.WrongChangeAttributeError,
                          fact_1.change, xxx='yyy')


    def test_uid_not_setupped(self):
        self.assertEqual(facts.Fact().uid, '#fact()')


    def test_has_money(self):
        has_money_1 = facts.HasMoney(object='hero', money=2)
        has_money_2 = facts.HasMoney(object='hero', money=20)

        self.assertFalse(has_money_1.check(self.kb))
        self.assertFalse(has_money_2.check(self.kb))

        self.kb += has_money_1

        self.assertTrue(has_money_1.check(self.kb))
        self.assertFalse(has_money_2.check(self.kb))
