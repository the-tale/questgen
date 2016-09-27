# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Fact, Place, Person, FACTS
from questgen import exceptions
from questgen import restrictions

class KnowledgeBaseTests(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()

        self.fact = Fact(uid='fact')
        self.fact_2 = Fact(uid='fact_2', description='cba')

        self.kb += [ self.fact,
                     self.fact_2 ]

    def test_serialize(self):
        self.assertEqual(self.kb.serialize(), KnowledgeBase.deserialize(self.kb.serialize(), FACTS).serialize())
        self.assertEqual(self.kb.serialize(short=True), KnowledgeBase.deserialize(self.kb.serialize(short=True), FACTS).serialize())
        self.assertNotEqual(self.kb.serialize(), KnowledgeBase.deserialize(self.kb.serialize(short=True), FACTS).serialize())

    def test_contains__for_child(self):
        self.assertTrue('fact' in self.kb)
        self.assertFalse('wrong uid' in self.kb)

    def test_getitem__for_child(self):
        self.assertEqual(self.kb['fact'].uid, 'fact')
        self.assertRaises(exceptions.NoFactError, self.kb.__getitem__, 'wrong uid')

    def test_get__for_child(self):
        self.assertEqual(self.kb.get('fact').uid, 'fact')
        self.assertEqual(self.kb.get('wrong uid'), None)

    def test_delitem__no_item(self):
        self.assertRaises(exceptions.NoFactError, self.kb.__delitem__, 'wrong_fact')

    def test_delitem(self):
        del self.kb['fact']
        self.assertFalse('fact' in self.kb)

    def test_add_fact__list(self):
        self.kb += [Fact(uid='fact 1'), Fact(uid='fact 2')]
        self.assertTrue('fact 1' in self.kb)
        self.assertTrue('fact 2' in self.kb)

    def test_add_fact__duplicate_fact(self):
        self.assertRaises(exceptions.DuplicatedFactError,
                          self.kb.__iadd__, self.fact)

    def test_add_fact__wrong_type(self):
        self.assertRaises(exceptions.WrongFactTypeError,
                          self.kb.__iadd__, 'some string')

    def test_add_fact__wrong_type_for_nested_lists(self):
        self.assertRaises(exceptions.WrongFactTypeError,
                          self.kb.__iadd__, [[Fact(uid='some fact')]])

    def test_remove_fact__no_fact(self):
        self.assertRaises(exceptions.NoFactError,
                          self.kb.__isub__, Fact(uid='some fact'))

    def test_remove_fact__wrong_type(self):
        self.assertRaises(exceptions.WrongFactTypeError,
                          self.kb.__isub__, 'some string')

    def test_remove_fact__wrong_type_for_nested_lists(self):
        self.assertRaises(exceptions.WrongFactTypeError,
                          self.kb.__isub__, [[self.fact]])

    def test_validate_consistency__success(self):
        self.kb.validate_consistency([])
        self.kb.validate_consistency([restrictions.AlwaysSuccess()])

    def test_validate_consistency__error(self):
        self.assertRaises(restrictions.AlwaysError.Error, self.kb.validate_consistency, [restrictions.AlwaysError()])

    def test_uids(self):
        self.assertEqual(self.kb.uids(),
                         set(self.kb._facts.keys()))

    def test_facts(self):
        self.assertEqual(set(fact.uid for fact in self.kb.facts()),
                         set(self.kb._facts.keys()))

    def test_filter__no_facts(self):
        self.assertEqual(list(self.kb.filter(Person)), [])

    def test_filter(self):
        self.assertEqual(len(list(self.kb.filter(Fact))), 2)

        person_1 = Person(uid='person_1')
        person_2 = Person(uid='person_2')
        place_1 = Place(uid='place_1')

        self.kb += [ person_1, person_2, place_1]

        self.assertEqual(len(list(self.kb.filter(Fact))), 5)
        self.assertEqual(set(fact.uid for fact in self.kb.filter(Person)),
                         set([person_1.uid, person_2.uid]))
        self.assertEqual(set(fact.uid for fact in self.kb.filter(Place)),
                         set([place_1.uid]))
