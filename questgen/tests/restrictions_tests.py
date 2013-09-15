# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Start, LocatedIn, Person, State, Jump, Finish
from questgen.restrictions import (AlwaysSuccess,
                                   AlwaysError,
                                   SingleStartState,
                                   NoJumpsFromFinish,
                                   SingleLocationForObject,
                                   ReferencesIntegrity,
                                   ConnectedStateJumpGraph,
                                   NoCirclesInStateJumpGraph)

class RestrictionsTestsBase(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()


class CommonRestrictionsTests(RestrictionsTestsBase):

    def test_always_success(self):
        AlwaysSuccess(knowledge_base=self.kb).validate()

    def test_always_error(self):
        restriction = AlwaysError(knowledge_base=self.kb)
        self.assertRaises(AlwaysError.Error, restriction.validate)


class SingleStartStateTests(RestrictionsTestsBase):

    def setUp(self):
        super(SingleStartStateTests, self).setUp()
        self.start = Start()
        self.restriction = SingleStartState(knowledge_base=self.kb)

    def test_success(self):
        self.kb += self.start
        self.restriction.validate()

    def test_no_start(self):
        self.assertRaises(SingleStartState.Error, self.restriction.validate)

    def test_more_then_one_start(self):
        self.kb += self.start,
        self.assertRaises(Exception, self.kb.__iadd__, Start())


class NoJumpsFromFinishTests(RestrictionsTestsBase):

    def setUp(self):
        super(NoJumpsFromFinishTests, self).setUp()
        self.kb += [Start(),
                    Finish(uid='finish_1'),
                    Jump(state_from=Start.UID, state_to='finish_1')]
        self.restriction = NoJumpsFromFinish(knowledge_base=self.kb)

    def test_success(self):
        self.restriction.validate()

    def test_error(self):
        self.kb += Jump(state_from='finish_1', state_to=Start.UID)
        self.assertRaises(NoJumpsFromFinish.Error, self.restriction.validate)


class SingleLocationForObjectTests(RestrictionsTestsBase):

    def setUp(self):
        super(SingleLocationForObjectTests, self).setUp()
        self.restriction = SingleLocationForObject(knowledge_base=self.kb)

    def test_success(self):
        self.kb += LocatedIn(object='person', place='place')
        self.restriction.validate()

    def test_no_location(self):
        self.restriction.validate()

    def test_more_then_one_location__for_person(self):
        self.kb += [ LocatedIn(object='person', place='place'),
                     LocatedIn(object='person', place='place_2')]
        self.assertRaises(SingleLocationForObject.Error, self.restriction.validate)

    def test_more_then_one_location__for_place(self):
        self.kb += [ LocatedIn(object='person', place='place'),
                     LocatedIn(object='person_2', place='place')]
        self.restriction.validate()


class ReferencesIntegrityTests(RestrictionsTestsBase):

    def setUp(self):
        super(ReferencesIntegrityTests, self).setUp()
        self.restriction = ReferencesIntegrity(knowledge_base=self.kb)

    def test_success(self):
        self.restriction.validate()

    def test_none_value(self):
        self.kb += [Person(uid='person'),
                    LocatedIn(object='person', place=None) ]
        self.restriction.validate()

    def test_bad_reference(self):
        self.kb += LocatedIn(object='person', place=None)
        self.assertRaises(ReferencesIntegrity.Error, self.restriction.validate)


class ConnectedStateJumpGraphTests(RestrictionsTestsBase):

    def setUp(self):
        super(ConnectedStateJumpGraphTests, self).setUp()
        self.restriction = ConnectedStateJumpGraph(knowledge_base=self.kb)

        self.kb += [Start(),
                    State(uid='state_1'),
                    State(uid='state_2'),
                    Finish(uid='finish_1'),
                    Finish(uid='finish_2'),
                    Jump(state_from=Start.UID, state_to='state_1'),
                    Jump(state_from='state_1', state_to='state_2'),
                    Jump(state_from='state_1', state_to='finish_1'),
                    Jump(state_from='state_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate()

    def test_state_not_reached(self):
        self.kb += [State(uid='state_3'),
                    State(uid='state_4'),
                    Jump(state_from='state_3', state_to='state_4')]
        self.assertRaises(ConnectedStateJumpGraph.Error, self.restriction.validate)


class NoCirclesInStateJumpGraphTests(RestrictionsTestsBase):

    def setUp(self):
        super(NoCirclesInStateJumpGraphTests, self).setUp()
        self.restriction = NoCirclesInStateJumpGraph(knowledge_base=self.kb)

        self.kb += [Start(),
                    State(uid='state_1'),
                    State(uid='state_2'),
                    State(uid='state_3'),
                    Finish(uid='finish_1'),
                    Jump(state_from=Start.UID, state_to='state_1'),
                    Jump(state_from='state_1', state_to='state_2'),
                    Jump(state_from='state_2', state_to='state_3'),
                    Jump(state_from='state_3', state_to='finish_1')]

    def test_success(self):
        self.restriction.validate()

    def test_state_not_reached(self):
        self.kb += Jump(state_from='state_3', state_to='state_1')
        self.assertRaises(NoCirclesInStateJumpGraph.Error, self.restriction.validate)
