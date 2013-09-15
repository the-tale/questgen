# coding: utf-8

from collections import Iterable

from questgen.facts import Fact
from questgen.restrictions import Restriction

from questgen import exceptions

class KnowledgeBase(object):

    def __init__(self):
        self._facts = {}
        self.restrictions = []

    def serialize(self):
        return {'facts': [fact.serialize() for fact in self._facts.values()],
                'restrictions': [restriction.serialize() for restriction in self.restrictions.values()]}

    @classmethod
    def deserialize(cls, data, restrictions, fact_classes):
        kb = cls()

        for fact_data in data['facts']:
            kb += fact_classes[fact_data['type']].deserialize(fact_data)

        kb += restrictions


    def __iadd__(self, fact, expected_fact=False):
        if isinstance(fact, Iterable) and not expected_fact:
            map(lambda element: self.__iadd__(element, expected_fact=True), fact)
        elif isinstance(fact, Fact):
            if fact.uid in self:
                raise exceptions.DuplicatedFactError(fact=fact)
            self._facts[fact.uid] = fact
        elif isinstance(fact, Restriction):
            fact.knowledge_base = self
            self.restrictions.append(fact)
        else:
            raise exceptions.WrongFactTypeError(fact=fact)

        return self

    def __isub__(self, fact, expected_fact=False):
        if isinstance(fact, Iterable) and not expected_fact:
            map(lambda element: self.__isub__(element, expected_fact=True), fact)
        elif isinstance(fact, Fact):
            del self[fact.uid]
        else:
            raise exceptions.WrongFactTypeError(fact=fact)

        return self

    def __contains__(self, fact_uid):
        return fact_uid in self._facts

    def __getitem__(self, fact_uid):
        if fact_uid in self._facts: return self._facts[fact_uid]
        raise exceptions.NoFactError(fact=fact_uid)

    def __delitem__(self, fact_uid):
        if fact_uid not in self:
            raise exceptions.NoFactError(fact=fact_uid)
        del self._facts[fact_uid]

    def get(self, fact_uid, default=None):
        if fact_uid in self._facts: return self._facts[fact_uid]
        return default

    def validate_consistency(self):
        for restriction in self.restrictions:
            restriction.validate()

    def uids(self):
        return set(self._facts.keys())

    def facts(self):
        return (self[fact_uid] for fact_uid in self.uids())

    def filter(self, fact_type):
        return (fact for fact in self.facts() if isinstance(fact, fact_type))
