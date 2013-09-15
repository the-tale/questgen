# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen import exceptions
from questgen.facts import Fact, LocatedIn


class FactsTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

    def test_check(self):
        fact = Fact(uid='fact_uid')
        self.assertFalse(fact.check(self.kb))
        self.kb += fact
        self.assertTrue(fact.check(self.kb))

    def test_change(self):
        fact_1 = LocatedIn(object='person_1', place='place_1')
        fact_2 = fact_1.change(place='place_2')
        self.assertEqual(fact_2.object, 'person_1')
        self.assertEqual(fact_2.place, 'place_2')

    def test_change__wrong_change_attribute(self):
        fact_1 = LocatedIn(object='person_1', place='place_1')
        self.assertRaises(exceptions.WrongChangeAttributeError,
                          fact_1.change, xxx='yyy')

    # def test_wrong_option_uid(self):
    #     self.assertRaises(exceptions.OptionUIDWithoutChoicePart,
    #                       Option, uid='choice_option', choice='choice', state_from='rt_nh', state_to='ht_spying')



    def test_uid_not_setupped(self):
        fact = Fact()
        self.assertRaises(exceptions.UIDDidNotSetupped, fact.update_uid)
