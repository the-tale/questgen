# coding: utf-8

import unittest

from questgen.knowledge_base import KnowledgeBase
from questgen.facts import Start, LocatedIn, LocatedNear, Person, State, Jump, Finish, Choice, Option
from questgen import restrictions

class RestrictionsTestsBase(unittest.TestCase):

    def setUp(self):
        self.kb = KnowledgeBase()


class CommonRestrictionsTests(RestrictionsTestsBase):

    def test_always_success(self):
        restrictions.AlwaysSuccess().validate(self.kb)

    def test_always_error(self):
        self.assertRaises(restrictions.AlwaysError.Error, restrictions.AlwaysError().validate, self.kb)


class SingleStartStateTests(RestrictionsTestsBase):

    def setUp(self):
        super(SingleStartStateTests, self).setUp()
        self.start = Start(uid='start', type='test')
        self.restriction = restrictions.SingleStartState()

    def test_success(self):
        self.kb += self.start
        self.restriction.validate(self.kb)

    def test_no_start(self):
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_start(self):
        self.kb += self.start,
        self.assertRaises(Exception, self.kb.__iadd__, Start(uid='start', type='test'))


class NoJumpsFromFinishTests(RestrictionsTestsBase):

    def setUp(self):
        super(NoJumpsFromFinishTests, self).setUp()
        self.kb += [Start(uid='start', type='test'),
                    Finish(uid='finish_1'),
                    Jump(state_from='start', state_to='finish_1')]
        self.restriction = restrictions.NoJumpsFromFinish()

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_error(self):
        self.kb += Jump(state_from='finish_1', state_to='start')
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class SingleLocationForObjectTests(RestrictionsTestsBase):

    def setUp(self):
        super(SingleLocationForObjectTests, self).setUp()
        self.restriction = restrictions.SingleLocationForObject()

    def test_success(self):
        self.kb += LocatedIn(object='person', place='place')
        self.restriction.validate(self.kb)

    def test_no_location(self):
        self.restriction.validate(self.kb)

    def test_more_then_one_location__for_person(self):
        self.kb += [ LocatedIn(object='person', place='place'),
                     LocatedIn(object='person', place='place_2')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_location__for_person__diferent_relations(self):
        self.kb += [ LocatedIn(object='person', place='place'),
                     LocatedNear(object='person', place='place_2')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)

    def test_more_then_one_location__for_place(self):
        self.kb += [ LocatedIn(object='person', place='place'),
                     LocatedIn(object='person_2', place='place')]
        self.restriction.validate(self.kb)

    def test_more_then_one_location__for_place__diferent_relations(self):
        self.kb += [ LocatedNear(object='person', place='place'),
                     LocatedIn(object='person_2', place='place')]
        self.restriction.validate(self.kb)


class ReferencesIntegrityTests(RestrictionsTestsBase):

    def setUp(self):
        super(ReferencesIntegrityTests, self).setUp()
        self.restriction = restrictions.ReferencesIntegrity()

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_none_value(self):
        self.kb += [Person(uid='person'),
                    LocatedIn(object='person', place=None) ]
        self.restriction.validate(self.kb)

    def test_bad_reference(self):
        self.kb += LocatedIn(object='person', place=None)
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class ConnectedStateJumpGraphTests(RestrictionsTestsBase):

    def setUp(self):
        super(ConnectedStateJumpGraphTests, self).setUp()
        self.restriction = restrictions.ConnectedStateJumpGraph()

        self.kb += [Start(uid='start', type='test'),
                    State(uid='state_1'),
                    State(uid='state_2'),
                    Finish(uid='finish_1'),
                    Finish(uid='finish_2'),
                    Jump(state_from='start', state_to='state_1'),
                    Jump(state_from='state_1', state_to='state_2'),
                    Jump(state_from='state_1', state_to='finish_1'),
                    Jump(state_from='state_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_state_not_reached(self):
        self.kb += [State(uid='state_3'),
                    State(uid='state_4'),
                    Jump(state_from='state_3', state_to='state_4')]
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class NoCirclesInStateJumpGraphTests(RestrictionsTestsBase):

    def setUp(self):
        super(NoCirclesInStateJumpGraphTests, self).setUp()
        self.restriction = restrictions.NoCirclesInStateJumpGraph()

        self.kb += [Start(uid='start', type='test'),
                    State(uid='state_1'),
                    State(uid='state_2'),
                    State(uid='state_3'),
                    Finish(uid='finish_1'),
                    Jump(state_from='start', state_to='state_1'),
                    Jump(state_from='state_1', state_to='state_2'),
                    Jump(state_from='state_2', state_to='state_3'),
                    Jump(state_from='state_3', state_to='finish_1')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_state_not_reached(self):
        self.kb += Jump(state_from='state_3', state_to='state_1')
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class MultipleJumpsFromNormalStateTests(RestrictionsTestsBase):

    def setUp(self):
        super(MultipleJumpsFromNormalStateTests, self).setUp()
        self.restriction = restrictions.MultipleJumpsFromNormalState()

        self.kb += [Start(uid='start', type='test'),
                    Choice(uid='state_1'),
                    State(uid='state_2'),
                    Finish(uid='finish_1'),
                    Finish(uid='finish_2'),
                    Jump(state_from='start', state_to='state_1'),
                    Option(state_from='state_1', state_to='state_2', type='opt_1'),
                    Option(state_from='state_1', state_to='finish_1', type='opt_2'),
                    Jump(state_from='state_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_state_not_reached(self):
        self.kb += Jump(state_from='state_2', state_to='finish_1')
        self.assertRaises(self.restriction.Error, self.restriction.validate, self.kb)


class ChoicesConsistencyTests(RestrictionsTestsBase):

    def setUp(self):
        super(ChoicesConsistencyTests, self).setUp()
        self.restriction = restrictions.ChoicesConsistency()

        self.kb += [Start(uid='start', type='test'),
                    Choice(uid='state_1'),
                    State(uid='state_2'),
                    Finish(uid='finish_1'),
                    Finish(uid='finish_2'),
                    Jump(state_from='start', state_to='state_1'),
                    Option(state_from='state_1', state_to='state_2', type='opt_1'),
                    Option(state_from='state_1', state_to='finish_1', type='opt_2'),
                    Jump(state_from='state_2', state_to='finish_2')]

    def test_success(self):
        self.restriction.validate(self.kb)

    def test_option_like_jump(self):
        self.kb += Option(state_from='state_2', state_to='finish_1', type='opt_3')
        self.assertRaises(self.restriction.OptionLikeJumpError, self.restriction.validate, self.kb)

    def test_jump_like_option(self):
        self.kb += Jump(state_from='state_1', state_to='finish_1')
        self.assertRaises(self.restriction.JumpLikeOptionError, self.restriction.validate, self.kb)
