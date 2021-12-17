
from collections.abc import Iterable

from questgen.facts import Fact

from questgen import exceptions

class KnowledgeBase(object):

    __slots__ = ('_facts', 'restrictions', 'ns_number')

    def __init__(self):
        self._facts = {}
        self.restrictions = []
        self.ns_number = 0

    def serialize(self, short=False):
        return {'facts': {fact.uid: fact.serialize(short=short) for fact in self._facts.values()},
                'ns_number': self.ns_number}

    @classmethod
    def deserialize(cls, data, fact_classes):
        kb = cls()

        for fact_data in data['facts'].values():
            kb += fact_classes[fact_data['type']].deserialize(fact_data)

        kb.ns_number = data['ns_number']

        return kb

    def get_next_ns(self):
        ns = '[ns-%d]' % self.ns_number
        self.ns_number += 1
        return ns


    def __iadd__(self, fact, expected_fact=False):
        if isinstance(fact, Iterable) and not expected_fact:
            for element in fact:
                self.__iadd__(element, expected_fact=True)
        elif isinstance(fact, Fact):
            if fact.uid in self:
                raise exceptions.DuplicatedFactError(fact=fact)
            self._facts[fact.uid] = fact
        else:
            raise exceptions.WrongFactTypeError(fact=fact)

        return self

    def __isub__(self, fact, expected_fact=False):
        if isinstance(fact, Iterable) and not expected_fact:
            for element in fact:
                self.__isub__(element, expected_fact=True)
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

    def validate_consistency(self, restrictions):
        for restriction in restrictions:
            restriction.validate(self)

    def uids(self):
        return set(self._facts.keys())

    def facts(self):
        return (self[fact_uid] for fact_uid in self.uids())

    def filter(self, fact_type):
        return (fact for fact in self.facts() if isinstance(fact, fact_type))

    def tagged(self, tag):
        return (fact for fact in self.facts() if tag in fact.tags)
